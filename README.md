# ClinicLink — evening transcription → minute-in escalation

**Code for a Billion — Bharat Agentic-AI Hackathon 2026 · Impact area: Health
(frontline health workers) · Entry status: PROTOTYPE REFINED + DEMO-READY,
NOT SUBMITTED, NOT DEPLOYED**

Nothing new. Something missing.

## The story — the specific gap, not a generic form

A frontline health worker walks village lanes with a paper register. She
sees a household, writes the visit down by hand, and walks on. Hours
later — sometimes a day later — back at the clinic, she transcribes it
all again onto the clinic laptop. Two copies of the same work, errors
creeping in at the second copy, and worst of all: if she saw a danger
sign in the morning, the clinic only learns about it in the evening.

The clinic laptop was never the problem. The distance was. The worker's
phone could not reach it from the field — not without accounts,
subscriptions, or being on the same Wi-Fi, none of which fit a rural
clinic.

ClinicLink closes that one gap, and only that gap: **evening
transcription becomes minute-in escalation.** The worker files from
the field, the clinic laptop sees it the same minute, and a danger-sign
tick becomes an unmissable red escalation banner. That is the whole
pitch — not "visit reporting", which any form can do.

## Why this is not generic visit-reporting

- **Time, not fields.** The differentiator is the time between a danger
  sign being seen and the clinic knowing: hours (paper, evening
  transcription) → the same minute (phone filing, dashboard banner).
- **Offline-first, laptop-as-host.** Records stay on the clinic laptop
  (local SQLite, no central cloud, no subscription). The phone is the
  controller; the laptop is the host. No account, no same-Wi-Fi
  requirement is assumed for the clinic model — the demo runs on one
  host and the pairing gate is what makes a phone trusted.
- **Approval-pairing, not an open form.** Request → clinic approves
  with a short code → token → instant revoke. Nothing files before a
  human approves, and filing stops the moment a token is revoked.
- **One escalation output, tick-driven only.** A checklist tick — and
  only a tick — produces "escalate per protocol". Free-text notes never
  escalate on their own and are never auto-diagnosed. That rule is what
  makes the banner trustworthy enough to be unmissable.

## What it does

1. **Approval-gated pairing.** The phone requests pairing; the clinic
   side approves with a short code. No token exists before a human
   approves, and any token can be revoked instantly.
2. **Visit report from the field (mobile-first phone view).** Household,
   visit type, a short note, and a danger-sign checklist (pregnancy,
   newborn, general), with large tap targets and a SYNTHETIC label on
   every screen.
3. **Structuring, not diagnosis.** The report is structured into a
   record. If — and only if — a danger sign is ticked, the record is
   flagged **"escalate per protocol"**. That is a prompt to follow the
   clinic's own protocol. It is never a diagnosis and never treatment
   advice. Free-text notes are stored verbatim and never auto-diagnosed.
4. **Clinic dashboard (separate view).** Today's visits filed,
   escalations flagged, households seen — as cards, not a JSON dump —
   with the red escalation banner listing today's escalated households
   at the top. Switch views with the Phone / Clinic tabs.
5. **Records stay on the clinic laptop.** Local SQLite, not a central
   health cloud. No trackers, no subscription.

## Honest-limits card — read before judging

- **Synthetic data only.** Every demo household is labelled synthetic.
  No real patient data has touched this code, and none should.
- **No real clinic deployment yet.** This is a working prototype plus a
  written pilot protocol (see below), not field evidence. Under the
  official rubric, Proven impact (25%) is therefore capped — a demo-only
  entry realistically competes for the other ~75 points. We say so in
  the submission rather than inventing field data.
- **Pairing model, not production keys.** The prototype models approval
  pairing with stdlib HMAC tokens. Abhiverse's production primitive is
  Ed25519 device keys; wiring real Ed25519 keys in is a documented next
  step, not a claim made here.
- **Structuring is deterministic rules in this build.** It validates and
  structures; it calls no model API and no paid service. The AgentFoundry
  agent step (LLM structuring producing this same record shape) is the
  user's remaining step — see AGENTFOUNDRY_IMPORT_GUIDE.md and
  SUBMISSION_CHECKLIST.md. This build does not claim to already be
  "built in AgentFoundry".
- **Not deployed yet.** The Render config in `render.yaml` is on paper
  only, now verified for free-tier shape (plan: free, `python3
  server.py`, `/health` health check, stdlib-only
  `requirements.txt`, `$PORT` handling in `server.py`). There is no
  live URL until the user deploys it himself, and no live link is
  claimed anywhere in this repo.
- **Separate module, not Abhiverse itself.** This repo is the entry that
  would be released open-source (MIT) to the Code for India org with
  attribution, per the hackathon's IP terms. Abhiverse itself stays in
  its own repo and is untouched by this build.

## Run it locally (free, no accounts, no keys)

```bash
cd cliniclink
python3 server.py          # http://127.0.0.1:8000
```

Python 3.12+ standard library only — nothing to install. Open the page
on a phone-sized window, use the **Phone** tab: request pairing,
approve with the shown code, file a visit, tick a danger sign and watch
the red escalation banner appear. Switch to the **Clinic laptop** tab
for today's summary cards and the escalated-visits list. Revoke pairing
at any time to prove filing stops.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

22 tests (17 original + 5 new), covering: escalation only on a
checklist tick, note text never escalating on its own, unknown signs /
bad visit types / missing fields rejected, wrong approval codes never
pairing, revocation killing a token, store summary counts, and the full
HTTP flow (401 without pairing, pair → file → summary, synthetic seed)
— plus the refined UI (story text, phone + clinic views, revoke flow,
escalation banner data, synthetic labels, no external CDN assets) and
the Render config (free plan, start command, `/health` check, `$PORT`
handling, no secrets).

## API (all JSON)

| Method & path | Auth | What it does |
|---|---|---|
| `GET /health` | — | Status + `synthetic_only: true` |
| `GET /api/danger-signs` | — | Checklist catalogue |
| `POST /api/pair/request` | — | `{"device_id"}` → approval code (10 min) |
| `POST /api/pair/approve` | — | `{"device_id","approval_code"}` → token |
| `POST /api/pair/revoke` | — | `{"pairing_token"}` → revoked flag |
| `POST /api/visits` | `X-Pairing-Token` | File a report → record + escalation |
| `GET /api/visits` | — | Filed reports, newest first |
| `GET /api/summary` | — | Today's clinic summary |
| `POST /api/seed` | — | Load 3 labelled synthetic demo records |

## Deploy path (on paper — not done, now deploy-ready)

Render free tier, `python3 server.py`, via `render.yaml` (plan: free,
`healthCheckPath: /health`, stdlib-only `requirements.txt`, server
binds `0.0.0.0` and reads `$PORT` with local fallback to
`CLINICLINK_PORT`/`8000`). Free-tier caveats for judges: services sleep
after ~15 min idle (expect a ~60s cold start), and demo state is local
SQLite on an ephemeral disk, deliberately NOT managed Postgres (free
Postgres expires after 30 days) — so demo state resets on
restart/redeploy, which is intentional for synthetic data. Cloud Run is
OUT — it needs a card, and this entry is free-only. No live URL exists
until the user deploys it himself and verifies `/health` + pair → file
→ summary on the live URL.

## Pilot measurement plan (a plan, labelled as a plan)

Full plan: `PILOT_MEASUREMENT_PLAN.md` — **zero invented field data.**
In short: (0) clinician sign-off of the danger-sign list against local
protocol before any use; (1) a 2-week paper-parallel run, where phone
filing runs alongside the paper register and the two are compared, so
no record exists only on the phone; (2) only then a phone-first week.
Measured, if ever run: time from danger sign seen to clinic aware
(paper route vs. ClinicLink route), transcription differences counted
field by field, visits/workers/households reached as counts, and a
revocation drill. No step of this protocol has happened yet, and no
percentage improvement, error-rate reduction, or outcome claim may be
quoted from it until a real pilot produces real numbers with sample
sizes attached.

## Event facts (re-verified 2 Nov 2026, official pages)

- Event: Code for a Billion — Bharat Agentic-AI Hackathon 2026, Code for
  India — https://codeforindia.org/hackathon
- Submission hub: https://github.com/karlmehta/code-for-a-billion
- Judging: 4 criteria × 25% — Size, Severity, Quality, Proven impact
  (ties broken by Proven impact, then Size) —
  https://github.com/karlmehta/code-for-a-billion/blob/main/JUDGING.md
- Prizes: ₹18,00,000 total — ₹1,50,000 / ₹1,00,000 / ₹50,000 per track
- Deadline: deploy by 15 Nov 2026. **Time-of-day cutoff is NOT stated on
  the official page — target 14 Nov, do not assume 15 Nov 23:59.**
- Winners announced 5 Dec 2026. Entry is free.
- Scope this build follows: `../SCOPE.md` (read it; this README does not
  replace it).
