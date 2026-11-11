"""ClinicLink on Vercel — serverless entry point.

Reuses the existing stdlib ``server.Handler`` unchanged: Vercel's Python
runtime runs a ``BaseHTTPRequestHandler`` subclass named ``handler``.
Local and Render behaviour is untouched (``python3 server.py``).

State note (same honesty as the CageCheck adaptation): Vercel functions
are ephemeral and the deployed filesystem is read-only, so SQLite lives
in /tmp (the only writable path) and pairing tokens live in memory. A
cold instance therefore starts empty; filed visits are visible only
while that instance stays warm. Do not treat the live demo as durable
storage. See the README honest-limits card.
"""

import os
from pathlib import Path

# SQLite must live in /tmp on Vercel (the deployed filesystem is read-only).
os.environ.setdefault("CLINICLINK_DB", "/tmp/cliniclink.db")

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server import Handler  # noqa: E402


class handler(Handler):
    """Vercel Python runtime entry point (BaseHTTPRequestHandler subclass)."""
