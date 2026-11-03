"""ClinicLink tests — standard library unittest only. No network, no secrets.

Run from cliniclink/:  python3 -m unittest discover -s tests -v
"""

import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cliniclink.models import DANGER_SIGNS, structure_note  # noqa: E402
from cliniclink.pairing import PairingStore  # noqa: E402
from cliniclink.store import VisitStore  # noqa: E402


class TestStructuring(unittest.TestCase):
    def test_routine_when_no_danger_sign(self):
        r = structure_note("W1", "Synthetic Household 12", "general",
                           "Routine visit.", [])
        self.assertEqual(r.escalation, "routine")

    def test_any_danger_sign_escalates(self):
        for sign in ("fever", "heavy_bleeding", "difficulty_breathing"):
            r = structure_note("W1", "Synthetic Household 12", "pregnancy",
                               "Note.", [sign])
            self.assertEqual(r.escalation, "escalate_per_protocol")

    def test_note_text_never_creates_escalation(self):
        # A scary-sounding note with NO checklist tick must stay routine.
        # The checklist, not free text, drives escalation. Never a diagnosis.
        r = structure_note("W1", "Synthetic Household 12", "general",
                           "Household mentioned bleeding and fever.", [])
        self.assertEqual(r.escalation, "routine")

    def test_unknown_danger_sign_rejected(self):
        with self.assertRaises(ValueError):
            structure_note("W1", "H1", "general", "", ["not_a_real_sign"])

    def test_missing_household_rejected(self):
        with self.assertRaises(ValueError):
            structure_note("W1", "  ", "general", "", [])

    def test_bad_visit_type_rejected(self):
        with self.assertRaises(ValueError):
            structure_note("W1", "H1", "surgery", "", [])

    def test_every_catalogued_sign_is_valid(self):
        for signs in DANGER_SIGNS.values():
            for sign in signs:
                r = structure_note("W1", "H1", "general", "", [sign])
                self.assertEqual(r.escalation, "escalate_per_protocol")


class TestPairing(unittest.TestCase):
    def setUp(self):
        self.p = PairingStore()

    def test_no_token_before_approval(self):
        self.assertFalse(self.p.is_paired("anything"))
        self.p.request("PHONE-1")
        self.assertFalse(self.p.is_paired("anything"))

    def test_wrong_code_does_not_pair(self):
        req = self.p.request("PHONE-1")
        with self.assertRaises(ValueError):
            self.p.approve("PHONE-1", "000000" if req["approval_code"] != "000000" else "111111")
        self.assertFalse(self.p.is_paired("x"))

    def test_correct_code_pairs_and_revocation_kills_it(self):
        req = self.p.request("PHONE-1")
        out = self.p.approve("PHONE-1", req["approval_code"])
        self.assertTrue(self.p.is_paired(out["pairing_token"]))
        self.assertTrue(self.p.revoke(out["pairing_token"]))
        self.assertFalse(self.p.is_paired(out["pairing_token"]))

    def test_approve_without_request_fails(self):
        with self.assertRaises(ValueError):
            self.p.approve("PHONE-9", "123456")


class TestStore(unittest.TestCase):
    def setUp(self):
        self.store = VisitStore(":memory:")

    def test_add_and_summary_counts_escalations(self):
        self.store.add(structure_note("W1", "H1", "general", "", []))
        self.store.add(structure_note("W1", "H2", "pregnancy", "", ["fever"]))
        s = self.store.summary()
        self.assertEqual(s["visits_filed_today"], 2)
        self.assertEqual(s["escalations_flagged"], 1)
        self.assertEqual(len(s["escalated_visits"]), 1)

    def test_records_are_flagged_synthetic(self):
        rec = self.store.add(structure_note("W1", "H1", "general", "", []))
        self.assertTrue(rec["synthetic"])


class TestApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import server
        # Point the server module at an in-memory store for tests.
        server.STORE = VisitStore(":memory:")
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def _req(self, path, body=None, token=None):
        url = f"http://127.0.0.1:{self.port}{path}"
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method="POST" if body is not None else "GET")
        if data:
            req.add_header("Content-Type", "application/json")
        if token:
            req.add_header("X-Pairing-Token", token)
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_health_endpoint(self):
        status, data = self._req("/health")
        self.assertEqual(status, 200)
        self.assertEqual(data["status"], "ok")
        self.assertTrue(data["synthetic_only"])

    def test_visit_requires_pairing(self):
        status, _ = self._req("/api/visits", {"worker_id": "W1", "household": "H1",
                                              "visit_type": "general", "note": "",
                                              "danger_signs": []})
        self.assertEqual(status, 401)

    def test_full_flow_pair_then_file_then_summary(self):
        _, req = self._req("/api/pair/request", {"device_id": "TEST-PHONE"})
        _, appr = self._req("/api/pair/approve", {"device_id": "TEST-PHONE",
                                                  "approval_code": req["approval_code"]})
        token = appr["pairing_token"]
        status, filed = self._req("/api/visits", {"worker_id": "W1", "household": "H9",
                                                  "visit_type": "pregnancy", "note": "Demo.",
                                                  "danger_signs": ["fever"]}, token=token)
        self.assertEqual(status, 201)
        self.assertEqual(filed["escalation"], "escalate_per_protocol")
        status, summary = self._req("/api/summary")
        self.assertEqual(status, 200)
        self.assertGreaterEqual(summary["visits_filed_today"], 1)
        self.assertGreaterEqual(summary["escalations_flagged"], 1)

    def test_seed_endpoint_loads_synthetic_records(self):
        status, data = self._req("/api/seed", {})
        self.assertEqual(status, 200)
        self.assertEqual(data["seeded"], 3)
        self.assertTrue(all(v["synthetic"] for v in data["visits"]))


if __name__ == "__main__":
    unittest.main()
