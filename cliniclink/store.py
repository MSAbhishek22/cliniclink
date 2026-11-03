"""Local SQLite storage — records stay on the clinic laptop.

No managed database, no central cloud. The demo must NOT depend on a
managed Postgres instance (Render free Postgres expires after 30 days),
so this store is a plain SQLite file next to the server, or :memory:
for tests.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date

from .models import VisitReport

SCHEMA = """
CREATE TABLE IF NOT EXISTS visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id TEXT NOT NULL,
    household TEXT NOT NULL,
    visit_type TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    danger_signs TEXT NOT NULL DEFAULT '[]',
    escalation TEXT NOT NULL,
    synthetic INTEGER NOT NULL DEFAULT 1,
    created_on TEXT NOT NULL
);
"""


class VisitStore:
    def __init__(self, path: str = "cliniclink.db"):
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def add(self, report: VisitReport) -> dict:
        cur = self._conn.execute(
            "INSERT INTO visits (worker_id, household, visit_type, note,"
            " danger_signs, escalation, synthetic, created_on)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (report.worker_id, report.household, report.visit_type,
             report.note, json.dumps(report.danger_signs),
             report.escalation, 1 if report.synthetic else 0,
             date.today().isoformat()),
        )
        self._conn.commit()
        return self.get(cur.lastrowid)

    def get(self, visit_id: int) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM visits WHERE id = ?", (visit_id,)).fetchone()
        return self._row_to_dict(row) if row else None

    def list_all(self) -> list:
        rows = self._conn.execute(
            "SELECT * FROM visits ORDER BY id DESC").fetchall()
        return [self._row_to_dict(r) for r in rows]

    def summary(self) -> dict:
        """Daily summary for the clinic laptop view."""
        today = date.today().isoformat()
        rows = self._conn.execute(
            "SELECT * FROM visits WHERE created_on = ?", (today,)).fetchall()
        visits = [self._row_to_dict(r) for r in rows]
        escalations = [v for v in visits
                       if v["escalation"] == "escalate_per_protocol"]
        households = sorted({v["household"] for v in visits})
        return {
            "date": today,
            "visits_filed_today": len(visits),
            "escalations_flagged": len(escalations),
            "households_seen_today": households,
            "escalated_visits": escalations,
            "pending_follow_up_note": (
                "Households with an escalation flag need follow-up per"
                " clinic protocol. This summary never states a diagnosis."
            ),
        }

    @staticmethod
    def _row_to_dict(row) -> dict:
        d = dict(row)
        d["danger_signs"] = json.loads(d["danger_signs"])
        d["synthetic"] = bool(d["synthetic"])
        return d
