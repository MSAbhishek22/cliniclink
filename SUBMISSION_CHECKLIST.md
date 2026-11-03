# ClinicLink — submission checklist (USER steps — not done by the agent)

**Status: prototype built and tested locally. NOTHING below has been
done. Do not treat this file as a submission.**

Target: file by **14 Nov 2026**. The official deadline is 15 Nov 2026,
but the official page does NOT state a time-of-day cutoff — do not
assume 15 Nov 23:59. Winners announced 5 Dec 2026.

## Step 1 — AgentFoundry signup (you, in your browser)

- Follow `AGENTFOUNDRY_IMPORT_GUIDE.md` exactly — it is the honest
  version of this step, including what not to claim.
- Sign up at https://agentfoundry.me and create the ClinicLink project
  in the IDE.
- **STOP AT ONCE if signup asks for a card.** The official pages say
  "no credit card" and 1M smart-code tokens free, but the signup form
  itself was never tested by the agent (no accounts were created). A
  card demand is an instant NO-GO for this step — report it, do not
  enter card details, do not try a paid tier.
- Import this `cliniclink/` code into the AgentFoundry project and
  confirm the agent structuring step runs there producing the same
  record shape (worker, household, visit type, note, danger signs,
  escalation). **Eligibility requires "Built using AgentFoundry" — the
  local prototype alone does not satisfy that line yet. Be honest about
  this in the submission issue: say what was built locally and what
  AgentFoundry step you confirmed, in your own words.**

## Step 2 — Public GitHub repo (you)

- Create a NEW public repo for ClinicLink only (MIT licence — the
  `LICENSE` file here is already MIT). **Do NOT push Abhiverse itself
  to this repo.** Per the hackathon's IP terms, the entry is released
  open-source to the Code for India GitHub org with you retaining
  attribution — confirm the exact transfer mechanics at submission
  time; do not promise the whole Abhiverse codebase to CFI.
- Push exactly this `cliniclink/` folder (plus its README) to that repo.
- Check the README renders and the setup instructions work from a
  clean checkout.

## Step 3 — Deploy on Render free tier (you, in your browser)

- Sign up on Render and deploy from the new repo using `render.yaml`
  (web service, free plan, `python3 server.py`, `/health` health
  check, stdlib-only `requirements.txt`). The config was refined and
  test-checked locally in this round, but it is still on paper only —
  no live URL exists until you deploy it.
- **STOP AT ONCE if Render asks for a card.** Free tier must stay free;
  do not enter card details.
- Verify the live URL yourself: `/health` responds, the Phone tab flow
  (pair → file → escalation banner) and the Clinic tab dashboard work
  on the live URL, not just locally, and revoke blocks filing there too.
- Note for judges (already in the README): free services sleep after
  ~15 min idle, so a first visit may take ~60s to wake; demo state is
  local SQLite on an ephemeral disk and resets on restart/redeploy —
  intentional for synthetic data, not a bug to hide.
- Cloud Run is OUT — it requires a card. Do not use it for this entry.
- If Render balks for any other reason, fallbacks on paper only:
  Vercel Hobby for the web half, or Cloudflare Workers free for the API
  edge — both re-verified at deploy time, neither attempted yet.

## Step 4 — Demo video (you)

- Record following `DEMO_SCRIPT.md` (2–3 min). Upload to YouTube
  (free, unlisted or public — your choice).
- Every household on screen must be captioned SYNTHETIC DATA. No real
  patient data, no diagnosis claim, no faked live response — if the
  free service is asleep on camera, say so and cut to the warm response.

## Step 5 — Submission issue (you, in your browser)

- File the structured submission issue in
  https://github.com/karlmehta/code-for-a-billion (each submission
  becomes a public issue labelled `submission`).
- Fields to fill, honestly:
  - Team/project name: ClinicLink (solo, M S Abhishek — confirm the
    name spelling you want public before filing).
  - Impact area / track: Health — frontline health workers.
  - Problem statement, sharpened (not generic "visit reporting"):
    evening transcription → minute-in escalation. Paper register →
    late transcription → delayed danger-sign escalation; clinic laptop
    unreachable from the field without accounts/subscriptions/same-Wi-Fi.
    Differentiator: offline-first, laptop-as-host, approval-pairing.
    Size/severity numbers ONLY with a source you cite (e.g. the current
    NHM ASHA figure — look it up at filing time; the scope deliberately
    pastes no number without a source).
  - What was built + how AgentFoundry was used: describe Step 1 as you
    actually did it, following AGENTFOUNDRY_IMPORT_GUIDE.md. Do not
    claim an AgentFoundry build you did not do.
  - Repo URL: from Step 2. Demo URL: live Render link from Step 3
    and/or the video from Step 4.
  - Proven impact, stated honestly: working prototype + live deployment
    + scripted timing comparison (only numbers you actually measured) +
    written pilot measurement plan (PILOT_MEASUREMENT_PLAN.md — a plan,
    zero field data). Explicitly state: no real clinic deployment
    yet, no field data invented. A demo-only entry caps Proven impact
    (25%) — say so rather than letting judges discover it.
- After filing, save the issue URL. Only then is anything "submitted".

## What the agent deliberately did NOT do (and why)

- No AgentFoundry / Render / GitHub account created — accounts are the
  user's own, in his own browser, with his own credentials.
- Nothing submitted — submission needs the user's repo, deployment,
  video, and legal/IP confirmation, plus his own review of every word
  in the issue.
- No live deployment claimed — `render.yaml` is a config on paper, not
  a running service.
- No real health data, no secrets, no card details anywhere in this
  folder. If any step above asks for a card, that step stops.
