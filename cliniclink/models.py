"""Visit-report model and danger-sign catalogue.

Design rules (from SCOPE.md, followed exactly):
- Synthetic data only. Nothing here is a diagnosis or treatment advice.
- Escalation is driven ONLY by an explicit danger-sign checklist tick.
  Free-text notes are stored verbatim and never auto-diagnosed.
- Records are meant to live on the clinic laptop (local SQLite), not in a
  central cloud.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Danger signs, grouped by visit context. The wording is deliberately
# observational ("worker saw / household reported"), never diagnostic.
DANGER_SIGNS = {
    "pregnancy": [
        "heavy_bleeding",
        "severe_headache_or_blurred_vision",
        "fever",
        "convulsions",
        "reduced_fetal_movement",
        "swelling_face_or_hands",
    ],
    "newborn": [
        "difficulty_breathing",
        "fever_or_low_temperature",
        "poor_feeding",
        "umbilical_redness_or_discharge",
        "jaundice",
        "unusual_sleepiness_or_lethargy",
    ],
    "general": [
        "high_fever_more_than_3_days",
        "difficulty_breathing",
        "signs_of_dehydration",
        "persistent_vomiting",
        "severe_weakness_or_fainting",
    ],
}

# Flat catalogue for validation: sign id -> group.
SIGN_TO_GROUP = {
    sign: group for group, signs in DANGER_SIGNS.items() for sign in signs
}

VISIT_TYPES = (
    "pregnancy",
    "newborn",
    "general",
    "follow_up",
    "immunisation_reminder",
)

MAX_NOTE_CHARS = 2000


@dataclass
class VisitReport:
    """One filed visit report, after structuring."""

    worker_id: str
    household: str
    visit_type: str
    note: str = ""
    danger_signs: list = field(default_factory=list)
    synthetic: bool = True

    def validate(self) -> list:
        """Return a list of validation errors (empty = valid)."""
        errors = []
        if not self.worker_id or not self.worker_id.strip():
            errors.append("worker_id is required")
        if not self.household or not self.household.strip():
            errors.append("household is required")
        if self.visit_type not in VISIT_TYPES:
            errors.append(f"visit_type must be one of {sorted(VISIT_TYPES)}")
        if len(self.note) > MAX_NOTE_CHARS:
            errors.append(f"note must be at most {MAX_NOTE_CHARS} characters")
        unknown = [s for s in self.danger_signs if s not in SIGN_TO_GROUP]
        if unknown:
            errors.append(f"unknown danger_signs: {unknown}")
        return errors

    @property
    def escalation(self) -> str:
        """The ONLY escalation output. Never a diagnosis.

        - "escalate_per_protocol" if any danger sign is ticked.
        - "routine" otherwise.
        """
        return "escalate_per_protocol" if self.danger_signs else "routine"


def structure_note(worker_id: str, household: str, visit_type: str,
                   note: str, danger_signs: list) -> VisitReport:
    """The agent structuring step, demo form.

    Honest labelling: this demo structuring is deterministic rules only —
    it trims whitespace, validates, and copies the checklist through. It
    does NOT call any model API and does NOT infer anything from the note
    text. In the AgentFoundry build, an LLM agent step would sit here and
    produce the same record shape; the record shape and the escalation
    rule are what this prototype proves.
    """
    report = VisitReport(
        worker_id=worker_id.strip() if worker_id else "",
        household=household.strip() if household else "",
        visit_type=visit_type,
        note=re.sub(r"\s+", " ", note or "").strip(),
        danger_signs=list(danger_signs or []),
        synthetic=True,
    )
    errors = report.validate()
    if errors:
        raise ValueError("; ".join(errors))
    return report
