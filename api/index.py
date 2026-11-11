"""ClinicLink on Vercel — serverless entry point.

Reuses the existing stdlib ``server.Handler`` unchanged: Vercel's Python
runtime runs a ``BaseHTTPRequestHandler`` subclass named ``handler``.
Local and Render behaviour is untouched (``python3 server.py``).

Routing note: the rewrite in vercel.json sends every route to
``/api/index?path=<original>``, so the handler sees
``/api/index?path=health`` instead of ``/health``. This subclass
restores the original path before the shared handler routes it.

State note (same honesty as the CageCheck adaptation): Vercel functions
are ephemeral and the deployed filesystem is read-only, so SQLite lives
in /tmp (the only writable path) and pairing tokens live in memory. A
cold instance therefore starts empty; filed visits are visible only
while that instance stays warm. Do not treat the live demo as durable
storage. See the README honest-limits card.
"""

import os
import sys
import urllib.parse
from pathlib import Path

# SQLite must live in /tmp on Vercel (the deployed filesystem is read-only).
os.environ.setdefault("CLINICLINK_DB", "/tmp/cliniclink.db")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server import Handler  # noqa: E402


class handler(Handler):
    """Vercel Python runtime entry point (BaseHTTPRequestHandler subclass)."""

    def _restore_path(self):
        if self.path.startswith("/api/index"):
            query = urllib.parse.urlparse(self.path).query
            original = urllib.parse.parse_qs(query).get("path", [""])[0]
            self.path = "/" + original if original else "/"

    def do_GET(self):
        self._restore_path()
        super().do_GET()

    def do_POST(self):
        self._restore_path()
        super().do_POST()
