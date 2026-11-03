"""Approval-gated pairing, prototype model.

This models the Abhiverse concept (phone = controller, clinic laptop =
agent host, explicit approval, instant revocation) with Python's standard
library only: HMAC-SHA256 tokens and a short-lived numeric approval code.

HONEST LIMIT: this prototype does NOT use Ed25519 device keys — that is
the Abhiverse production primitive, and wiring real Ed25519 keys in is a
documented next step, not something this file pretends to do. The flow
it proves is the approval gate itself: no token exists until a human on
the clinic side approves the pairing request, and a token can be revoked
at any time.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time

CODE_TTL_SECONDS = 600  # approval codes live 10 minutes


class PairingStore:
    """In-memory pairing state. Tokens are not persisted in this demo."""

    def __init__(self, secret: bytes | None = None):
        self._secret = secret or secrets.token_bytes(32)
        self._pending: dict = {}   # device_id -> {"code": str, "expires": float}
        self._tokens: dict = {}    # token -> device_id
        self._revoked: set = set()

    def request(self, device_id: str) -> dict:
        """Start pairing. Returns a code the clinic side must approve."""
        if not device_id or not device_id.strip():
            raise ValueError("device_id is required")
        code = f"{secrets.randbelow(1_000_000):06d}"
        self._pending[device_id] = {
            "code": code,
            "expires": time.time() + CODE_TTL_SECONDS,
        }
        return {"device_id": device_id, "approval_code": code,
                "expires_in_seconds": CODE_TTL_SECONDS}

    def approve(self, device_id: str, approval_code: str) -> dict:
        """Clinic-side approval. Only a matching, unexpired code mints a token."""
        pending = self._pending.get(device_id)
        if pending is None:
            raise ValueError("no pending pairing request for this device")
        if time.time() > pending["expires"]:
            del self._pending[device_id]
            raise ValueError("approval code expired")
        if not hmac.compare_digest(pending["code"], approval_code or ""):
            raise ValueError("approval code does not match")
        del self._pending[device_id]
        token = hmac.new(
            self._secret,
            f"{device_id}:{secrets.token_hex(16)}".encode(),
            hashlib.sha256,
        ).hexdigest()
        self._tokens[token] = device_id
        return {"device_id": device_id, "pairing_token": token}

    def is_paired(self, token: str | None) -> bool:
        return bool(token) and token in self._tokens and token not in self._revoked

    def revoke(self, token: str) -> bool:
        """Instant revocation. Returns True if a live token was revoked."""
        if token in self._tokens and token not in self._revoked:
            self._revoked.add(token)
            return True
        return False
