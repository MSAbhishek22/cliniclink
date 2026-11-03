"""ClinicLink UI + deploy-config tests — stdlib unittest only, no network.

Run from cliniclink/:  python3 -m unittest discover -s tests -v
Covers the refined demo UI (phone + clinic views, escalation banner,
pairing revoke in the UI flow) and the Render deploy config on paper.
Nothing here deploys, submits, or uses real data.
"""

import json
import os
import sys
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cliniclink.store import VisitStore  # noqa: E402

HERE = Path(__file__).resolve().parent.parent


class TestUiPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import server
        server.STORE = VisitStore(":memory:")
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def _get(self, path):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}{path}") as r:
            return r.status, r.read().decode()

    def _req(self, path, body=None, token=None):
        url = f"http://127.0.0.1:{self.port}{path}"
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data,
                                     method="POST" if body is not None else "GET")
        if data:
            req.add_header("Content-Type", "application/json")
        if token:
            req.add_header("X-Pairing-Token", token)
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_homepage_is_demo_ready(self):
        status, html = self._get("/")
        self.assertEqual(status, 200)
        # Sharpened theme story, not a generic form.
        self.assertIn("Evening transcription", html)
        self.assertIn("minute", html)
        self.assertIn("escalate per protocol", html.lower())
        # Two views, pairing flow, dashboard, synthetic labels everywhere.
        self.assertIn("Phone", html)
        self.assertIn("Clinic laptop", html)
        self.assertIn("Revoke", html)
        self.assertIn("today", html.lower())
        self.assertGreaterEqual(html.count("SYNTHETIC"), 3)
        self.assertIn("never", html.lower())  # never a diagnosis
        # No external assets: offline-first demo must not depend on a CDN.
        self.assertNotIn("http://", html.replace("http://127.0.0.1", ""))
        self.assertNotIn("https://", html)

    def test_revoked_token_cannot_file_via_api(self):
        _, req = self._req("/api/pair/request", {"device_id": "UI-PHONE"})
        _, appr = self._req("/api/pair/approve", {"device_id": "UI-PHONE",
                                                  "approval_code": req["approval_code"]})
        token = appr["pairing_token"]
        status, _ = self._req("/api/pair/revoke", {"pairing_token": token})
        self.assertEqual(status, 200)
        status, _ = self._req("/api/visits", {"worker_id": "W1", "household": "H1",
                                              "visit_type": "general", "note": "",
                                              "danger_signs": []}, token=token)
        self.assertEqual(status, 401)

    def test_summary_lists_escalated_visits_for_banner(self):
        _, req = self._req("/api/pair/request", {"device_id": "UI-PHONE-2"})
        _, appr = self._req("/api/pair/approve", {"device_id": "UI-PHONE-2",
                                                  "approval_code": req["approval_code"]})
        self._req("/api/visits", {"worker_id": "W1", "household": "Synthetic H",
                                 "visit_type": "pregnancy", "note": "Demo.",
                                 "danger_signs": ["fever"]}, token=appr["pairing_token"])
        status, summary = self._req("/api/summary")
        self.assertEqual(status, 200)
        self.assertGreaterEqual(summary["escalations_flagged"], 1)
        self.assertTrue(any(v["escalation"] == "escalate_per_protocol"
                            for v in summary["escalated_visits"]))


class TestRenderConfig(unittest.TestCase):
    def test_render_yaml_is_free_and_port_aware(self):
        text = (HERE / "render.yaml").read_text()
        self.assertIn("plan: free", text)
        self.assertIn("python3 server.py", text)
        self.assertIn("healthCheckPath: /health", text)
        # Deploy is on paper only, and the config must not require a
        # managed database: state is local SQLite, deliberately ephemeral.
        self.assertIn("SQLite", text)
        self.assertIn("PORT", (HERE / "server.py").read_text())

    def test_no_secrets_or_real_data_in_repo_files(self):
        # Grep-level guard: no token/password placeholders with values.
        for path in [HERE / "server.py", HERE / "render.yaml",
                     HERE / "static" / "index.html"]:
            text = path.read_text()
            self.assertNotIn("api_key=", text.lower())
            self.assertNotIn("password=", text.lower())


if __name__ == "__main__":
    unittest.main()
