"""ClinicLink demo server — Python standard library only.

Run:  python3 server.py            (listens on 127.0.0.1:8000)
       CLINICLINK_PORT=8000 CLINICLINK_DB=cliniclink.db python3 server.py

Endpoints:
  GET  /health                 -> service status, synthetic-only flag
  GET  /                       -> phone + clinic demo UI
  GET  /api/danger-signs       -> checklist catalogue
  POST /api/pair/request       -> {"device_id"} -> approval code
  POST /api/pair/approve       -> {"device_id","approval_code"} -> token
  POST /api/pair/revoke        -> {"pairing_token"} -> revoked flag
  POST /api/visits             -> X-Pairing-Token required, files a report
  GET  /api/visits             -> filed reports (newest first)
  GET  /api/summary            -> today's clinic summary
  POST /api/seed               -> loads synthetic demo records (labelled)

No secrets, no real health data, no external API calls, no paid service.
Deploy note: Render free tier (see render.yaml) asks for a card at deploy
time, so the live demo runs on Vercel Hobby instead (see vercel.json and
api/index.py). Vercel functions are ephemeral and the deployed filesystem
is read-only, so SQLite lives in /tmp and filed visits are visible only
while an instance stays warm.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cliniclink.models import DANGER_SIGNS, structure_note  # noqa: E402
from cliniclink.pairing import PairingStore  # noqa: E402
from cliniclink.store import VisitStore  # noqa: E402

HERE = Path(__file__).parent
STATIC = HERE / "static"

PAIRING = PairingStore()
STORE = VisitStore(os.environ.get("CLINICLINK_DB") or ("/tmp/cliniclink.db" if os.environ.get("VERCEL") else "cliniclink.db"))

# Clearly synthetic demo households. No real person is represented here.
SYNTHETIC_SEED = [
    {"worker_id": "DEMO-WORKER-01", "household": "Synthetic Household 12",
     "visit_type": "pregnancy", "note": "Routine antenatal check-in, synthetic demo.",
     "danger_signs": []},
    {"worker_id": "DEMO-WORKER-01", "household": "Synthetic Household 07",
     "visit_type": "pregnancy", "note": "Household reported fever, synthetic demo.",
     "danger_signs": ["fever"]},
    {"worker_id": "DEMO-WORKER-01", "household": "Synthetic Household 03",
     "visit_type": "newborn", "note": "Newborn check-in, synthetic demo.",
     "danger_signs": []},
]


class Handler(BaseHTTPRequestHandler):
    server_version = "ClinicLink/0.1.0"

    def log_message(self, *args):  # keep demo output quiet
        pass

    def _send(self, payload, code=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        size = int(self.headers.get("Content-Length") or 0)
        if not size:
            return {}
        try:
            return json.loads(self.rfile.read(size) or b"{}")
        except (json.JSONDecodeError, ValueError):
            return {}

    def _paired(self) -> bool:
        return PAIRING.is_paired(self.headers.get("X-Pairing-Token"))

    def _restore_path(self):
        # Vercel rewrites every route to /api/index, so the handler sees
        # "/api/index?path=<original>" instead of the real path. The
        # rewrite in vercel.json carries the original path in the query
        # string; locally (python3 server.py) there is no rewrite and
        # self.path already is the real path.
        if self.path.startswith("/api/index"):
            original = urllib.parse.parse_qs(
                urllib.parse.urlparse(self.path).query
            ).get("path", [""])[0]
            self.path = "/" + original if original else "/"

    def do_GET(self):
        self._restore_path()
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            data = (STATIC / "index.html").read_bytes()
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        elif self.path == "/health":
            self._send(
                {
                    "status": "ok",
                    "service": "cliniclink",
                    "version": "0.1.0",
                    "synthetic_only": True,
                    "diagnosis": "never",
                }
            )
        elif self.path == "/api/danger-signs":
            self._send({"danger_signs": list(DANGER_SIGNS)})
        elif self.path == "/api/visits":
            self._send({"visits": [v.as_dict() for v in STORE.list_all()]})
        elif self.path == "/api/summary":
            self._send(STORE.summary())
        else:
            self._send({"error": "not found"}, 404)

    def do_POST(self):
        self._restore_path()
        body = self._read_json()

        if self.path == "/api/pair/request":
            result = PAIRING.request(body.get("device_id") or "")
            return self._send(result, 201 if "approval_code" in result else 400)

        if self.path == "/api/pair/approve":
            result = PAIRING.approve(body.get("device_id") or "", body.get("approval_code") or "")
            return self._send(result, 200 if "pairing_token" in result else 400)

        if self.path == "/api/pair/revoke":
            return self._send({"revoked": PAIRING.revoke(body.get("pairing_token") or "")})

        if self.path == "/api/seed":
            filed = [STORE.add(structure_note(**rec)) for rec in SYNTHETIC_SEED]
            return self._send({"seeded": len(filed), "visits": filed})

        if self.path == "/api/visits":
            if not self._paired():
                return self._send({"error": "not paired"}, 401)
            try:
                report = structure_note(
                    body.get("worker_id") or "",
                    body.get("household") or "",
                    body.get("visit_type") or "",
                    body.get("note") or "",
                    body.get("danger_signs") or [],
                )
            except ValueError as exc:
                return self._send({"error": str(exc)}, 400)
            return self._send(STORE.add(report), 201)

        return self._send({"error": "not found"}, 404)


def main():
    port = int(os.environ.get("PORT", os.environ.get("CLINICLINK_PORT", "8000")))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"ClinicLink demo on port {port}  (synthetic data only)")
    server.serve_forever()


if __name__ == "__main__":
    main()
