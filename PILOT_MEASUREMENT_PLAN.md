# ClinicLink pilot-measurement plan — PLAN ONLY, zero field data

**Status: this plan has not happened. No clinic, no NGO, no field worker
has used ClinicLink yet, and no number below is a result.** Every
"target" is a measurement definition, not a claim. If this plan is ever
run, its real numbers replace this file's blanks — nothing here may be
quoted as evidence until then.

## Why measurement matters for this entry

Judging is 4 × 25%: Size, Severity, Quality, Proven impact. Proven
impact is defined by the organisers as "actual deployment data — real
evidence of impact in the field (users reached, outcomes, measurable
change)", with ties broken by Proven impact first. A demo-only entry
therefore realistically competes for ~75 points. This plan is how a
future pilot would earn the fourth quarter honestly — it does not
pretend the pilot already exists.

## The sharpened gap being measured

Not "a better form". The gap is the **time between a danger sign being
seen in the field and the clinic laptop knowing about it**:

- Today (paper): seen in the morning → transcribed in the evening →
  clinic learns hours later, after a second copy step where errors
  creep in.
- With ClinicLink: filed from the field → visible on the clinic
  dashboard the same minute → danger-sign tick = unmissable
  escalation banner.

So the pilot measures time and transcription error, not "satisfaction"
or "engagement".

## Phase 0 — clinician sign-off (before any use, mandatory)

1. A clinician reviews the danger-sign catalogue in
   `cliniclink/models.py` against the local clinic protocol, line by
   line. Any sign not in local protocol is removed before use; any
   locally required sign is added through the same checklist rule
   (tick-only escalation, never free-text inference).
2. Written confirmation that "escalate per protocol" is understood as
   a prompt to follow protocol — never a diagnosis, never treatment
   advice — and that the clinic, not the app, decides follow-up.
3. Data rule confirmed: synthetic demo data is wiped; only the pilot
   clinic's own consented records are filed, on the clinic laptop only,
   under the clinic's own data handling. No central cloud, no
   subscription, no record leaves the laptop without the clinic's
   decision.

If Phase 0 is not signed off, the pilot does not start. No exceptions.

## Phase 1 — paper-parallel run (2 weeks, proposed)

Phone filing runs **alongside** the paper register, never instead of
it, so no record exists only on the phone. Each visit therefore has
two timestamps the pilot can compare honestly:

| Metric | Definition (exactly how it is timed) | What counts |
|---|---|---|
| Time to clinic awareness (paper) | From the worker noting the visit in the field to the paper entry being transcribed onto the clinic laptop and seen by clinic staff | Clock times written on the paper form + transcription log |
| Time to clinic awareness (ClinicLink) | From the worker tapping "File report" to the record appearing on the clinic dashboard | Server timestamp of the filed record vs. dashboard refresh log |
| Transcription errors avoided | Paper copy vs. phone copy of the same visit, field by field (household, visit type, danger signs) | Count of fields that differ between the two copies, with the paper copy as the reference only where the clinic confirms it |
| Escalation lag (paper) | Danger sign seen → clinic staff aware via paper route | As above, for escalated visits only |
| Escalation lag (ClinicLink) | Danger sign ticked → escalation banner on the dashboard | As above, for escalated visits only |
| Filing burden | Minutes the worker spends filing per visit, each route | Stopwatch / self-logged, same worker, same visit types |

Record: number of visits, number of workers, number of households
seen, number of escalations — as counts only, with no patient-identifying
detail in any report or submission update.

## Phase 2 — phone-first week (only if Phase 1 is clean)

Only if Phase 1 shows no lost records and the clinic confirms the
phone copy matches paper: one week where phone filing is primary and
paper is the backup check. Same metrics as Phase 1, plus:

- Missed/lost reports: any visit the worker recalls filing that is
  not on the dashboard (target definition: zero unexplained losses;
  any loss pauses the pilot).
- Revocation drill: one paired phone revoked mid-week, confirming
  filing stops immediately (mirrors the demo's revoke test).

## What would be reported — and what would NOT

Reportable (only after a real pilot, with its dates and sample size):
visits filed, escalations flagged, median time-to-awareness for each
route, transcription differences counted, workers/households reached
as counts. Every number carries its sample size and its measurement
method.

Never reportable from this prototype: any percentage improvement,
any error-rate reduction, any "lives saved" or outcome claim, any
number copied from another project's pilot, or any field statistic
without a cited source and a real measurement behind it. A scripted
stopwatch comparison in the demo video (same synthetic household,
same fields, paper vs. phone, both times shown) is a demo illustration
only — it is not pilot evidence and must be labelled as such on camera.

## Honest current position (for the submission issue)

- Prototype: built, tested (22 tests), demo-ready, deploy-ready on paper.
- Pilot: not started. No field data exists. No Proven-impact points
  are claimed on the basis of this plan — the plan is the path to
  earning them, stated openly so judges can weigh it.
