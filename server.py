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
Deploy note (NOT done here): Render free tier, `python3 server.py`, with
PORT supplied by Render — see render.yaml. Free services sleep after
inactivity, so judges should expect a ~60s cold start; the demo video
shows the warm path.
"""

from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cliniclink.models import DANGER_SIGNS, structure_note  # noqa: E402
from cliniclink.pairing import PairingStore  # noqa: E402
from cliniclink.store import VisitStore  # noqa: E402

HERE = Path(__file__).parent
STATIC = HERE / "static"

PAIRING = PairingStore()
STORE = VisitStore(os.environ.get("CLINICLINK_DB", "cliniclink.db"))

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

    # -- helpers ---------------------------------------------------------
    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        try:
            data = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}
        return data if isinstance(data, dict) else {}

    def _paired(self) -> bool:
        return PAIRING.is_paired(self.headers.get("X-Pairing-Token"))

    # -- routes ----------------------------------------------------------
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            page = (STATIC / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)
        elif self.path == "/health":
            self._send(200, {"status": "ok", "service": "cliniclink",
                             "version": "0.1.0", "synthetic_only": True,
                             "diagnosis": "never"})
        elif self.path == "/api/danger-signs":
            self._send(200, {"danger_signs": DANGER_SIGNS})
        elif self.path == "/api/visits":
            self._send(200, {"visits": STORE.list_all()})
        elif self.path == "/api/summary":
            self._send(200, STORE.summary())
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        body = self._read_json()
        try:
            if self.path == "/api/pair/request":
                self._send(200, PAIRING.request(body.get("device_id", "")))
            elif self.path == "/api/pair/approve":
                self._send(200, PAIRING.approve(
                    body.get("device_id", ""), body.get("approval_code", "")))
            elif self.path == "/api/pair/revoke":
                token = body.get("pairing_token", "")
                self._send(200, {"revoked": PAIRING.revoke(token)})
            elif self.path == "/api/seed":
                filed = [STORE.add(structure_note(**rec))
                         for rec in SYNTHETIC_SEED]
                self._send(200, {"seeded": len(filed), "visits": filed})
            elif self.path == "/api/visits":
                if not self._paired():
                    self._send(401, {"error": "pairing required: approve a"
                                        " pairing first, then send"
                                        " X-Pairing-Token"})
                    return
                report = structure_note(
                    body.get("worker_id", ""), body.get("household", ""),
                    body.get("visit_type", ""), body.get("note", ""),
                    body.get("danger_signs", []))
                self._send(201, STORE.add(report))
            else:
                self._send(404, {"error": "not found"})
        except ValueError as exc:
            self._send(400, {"error": str(exc)})


def main() -> None:
    # Render supplies PORT; locally fall back to CLINICLINK_PORT or 8000.
    # Binding 0.0.0.0 is required on Render; locally it is still reached
    # at http://127.0.0.1:<port>.
    port = int(os.environ.get("PORT", os.environ.get("CLINICLINK_PORT", "8000")))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"ClinicLink demo on port {port}  (synthetic data only)")
    server.serve_forever()


if __name__ == "__main__":
    main()
