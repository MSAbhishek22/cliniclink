# ClinicLink — Deployment Runbook

**Project:** ClinicLink — evening transcription → minute-in escalation
**Entry:** Code for a Billion — Bharat Agentic-AI Hackathon 2026 (Code for India)
**Repo:** https://github.com/MSAbhishek22/cliniclink — commit `def70ad7`
  (at gate-file writing time; re-check the commit before deploying — the
  deployed SHA must be recorded in `deployment/RELEASE_MANIFEST.json` and
  must match the live build, Rulebook §6.1)
**Deployment status: NOT DEPLOYED.** Everything below is on paper, verified
against `render.yaml` and `server.py`, but no live URL exists. Do not claim
a live URL until the steps in §2 are actually done and §3 is actually run.
**Rulebook:** ABHI_22 Global Project Quality Rulebook v1.0, §5.

> **Hard boundaries:**
> - Synthetic data only, never a diagnosis, never real patient data.
> - Free tier only. **STOP AT ONCE if Render asks for a card.** Cloud Run
>   is OUT (it needs a card). No paid plan, no paid Postgres, no spending
>   without explicit user approval (Rulebook §11).
> - This runbook does NOT authorise creating a Render account, a GitHub
>   repo, or any credential on the user's behalf. Those are the user's
>   own-browser steps (see §2).

## 1. Architecture (what is actually deployed)

| Part | Choice (actual, from code/config) |
|---|---|
| Frontend + backend | One stdlib Python service: `server.py` serves `static/index.html` AND the JSON API from the same process. No separate frontend host, no build step, no CDN. |
| Hosting (planned) | Render, web service `cliniclink-demo`, `plan: free`, `env: python` |
| Build | `pip install -r requirements.txt \|\| echo 'stdlib only — nothing to install'` — `requirements.txt` is comments only (stdlib only). Note: the `\|\| echo` fallback exits 0 even if pip fails; a green build is NOT proof pip ran (harmless here, but stated). |
| Start | `python3 server.py` |
| Health check | `GET /health` → 200 `{"status":"ok","service":"cliniclink","version":"0.1.0","synthetic_only":true,"diagnosis":"never"}` |
| Port / binding | Server binds `0.0.0.0` and reads `$PORT` (Render supplies it), falling back to `$CLINICLINK_PORT`, then `8000`. Locally it is reached at `http://127.0.0.1:<port>`. |
| Storage | Local SQLite file (`cliniclink.db` by default, or `$CLINICLINK_DB`), on Render's ephemeral disk. **No managed Postgres** (free Postgres expires after 30 days, deliberately avoided). Consequence: demo state resets on restart/redeploy — intentional for synthetic data. |
| Pairing state | In-memory only (`cliniclink/pairing.py`, per-process HMAC secret). **NOT persisted.** A restart/redeploy invalidates every pairing token and every pending approval code. |
| Secrets | None. No API keys, no model calls, no paid service in this build. The AgentFoundry agent step (see `AGENTFOUNDRY_IMPORT_GUIDE.md`) is a separate user step with its own credentials, which must NEVER be committed or pasted into the repo/issue/chat. |
| External assets | None. No CDN, no webfont, no tracker (asserted by test `test_homepage_is_demo_ready`). |

## 2. Deploy steps (user, in his own browser — NOT done)

1. **Render signup (user).** Sign up at Render and link the GitHub repo
   `MSAbhishek22/cliniclink`. STOP AT ONCE if Render asks for a card
   or any payment method. Confirm in the Render dashboard that the
   service shows **plan: Free** before proceeding.
2. **Create the service from `render.yaml`.** Service name
   `cliniclink-demo`, type web, env python. `render.yaml` does NOT set
   branch, region, or auto-deploy fields — confirm those in the
   dashboard and record what was actually chosen in the release
   manifest. Do not assume defaults.
3. **Deploy and wait for "live".** A provider "deployment successful"
   message is NOT sufficient (Rulebook §5.2). Proceed to §3 and run
   every check on the live URL before claiming anything.
4. **Record the release.** Fill `deployment/RELEASE_MANIFEST.json` with
   the ACTUAL deployed commit SHA, provider, build/deployment id (if
   shown), production URL, and UTC+IST timestamps. The manifest in this
   folder currently has `deployed SHA: null, production URL: null`
   because nothing is deployed — that is the truthful state, not a
   placeholder to be quoted.

## 3. Live verification checklist (all on the live Render URL, in order)

**Warm the service first.** Free-tier sleep is real: ~15 min idle, then
a ~60s cold start. `healthCheckPath` is NOT a keep-alive. Warm the
service, then run the whole checklist in ONE warm session with NO
redeploy in between (pairing tokens die on restart).

1. `GET /health` → 200 with exactly: `status: ok, service: cliniclink,
   version: 0.1.0, synthetic_only: true, diagnosis: never`.
2. `GET /api/danger-signs` → catalogue loads (pregnancy/newborn/general).
3. `GET /` → Phone + Clinic tabs render, story "Evening transcription →
   minute-in escalation" visible, SYNTHETIC labels present (tests
   require ≥3), no external CDN assets.
4. (Optional) `POST /api/seed` → `seeded: 3`. Note: a fresh deploy has
   an EMPTY database — an empty dashboard on first load is NOT a
   failure, and must not be presented as the demo. Seed, or file
   fresh, before filming/judging.
5. `POST /api/visits` WITHOUT `X-Pairing-Token` → 401 `pairing required`.
6. `POST /api/pair/request` with a test `device_id` → 6-digit
   `approval_code`, `expires_in_seconds: 600`.
7. `POST /api/pair/approve` with that code WITHIN 10 minutes →
   `pairing_token`. Wrong code → error, no token. Expired code (>600s)
   → error, no token.
8. `POST /api/visits` WITH the token, pregnancy visit, household
   `Synthetic Household 07`, `danger_signs: ["fever"]` → 201,
   `escalation: escalate_per_protocol`.
9. A scary-sounding note with NO tick → 201, `escalation: routine`.
   (This is the trust test: note text never escalates.)
10. `GET /api/summary` → `escalations_flagged >= 1`, escalated visit listed.
11. Phone tab: pair stepper shows Paired, red ESCALATE PER PROTOCOL
    banner visible the same minute.
12. Clinic tab: summary cards, red banner, escalated visit with
    SYNTHETIC label.
13. `POST /api/pair/revoke` → `revoked: true`; filing with the same
    token afterwards → 401.
14. Re-pair and re-seed after ANY restart/redeploy (tokens and DB rows
    are gone), and re-run steps 5–13 if the deploy changed.

**If any step fails:** do not film around it, do not fake the response
with a local screenshot (see `submission/DEMO_VIDEO_MANIFEST.md`).
Fix, redeploy, and re-run the WHOLE checklist — a partial pass is not
a pass.

## 4. Environment variables (by NAME only — never values)

| Variable | Required? | Meaning |
|---|---|---|
| `PORT` | Supplied by Render | Port the server binds. |
| `CLINICLINK_PORT` | Local fallback only | Local port when `PORT` is absent. |
| `CLINICLINK_DB` | Optional | SQLite file path. Default `cliniclink.db` (relative to the WORKING DIRECTORY, not anchored to `server.py`'s directory — see §6). |
| `PYTHON_VERSION` | Set in `render.yaml` | `3.12.0`. |
| (No other env vars) | — | No API keys, no model keys, no secrets exist in this build. Do not invent any. |

## 5. Warm-before-filming / warm-before-judging note

- Warm the live service before filming the demo and before any judging
  session. If the service is asleep, say so on camera ("free tier wakes
  in about a minute") and cut to the warm response — do NOT fake a live
  response with a local screenshot (DEMO_SCRIPT.md Shot 4).
- The demo video MUST be re-recorded (or at minimum its live shot
  re-checked) from the live URL after deploy. The existing narrated
  video is NOT live-recorded — see `submission/DEMO_VIDEO_MANIFEST.md`.
- Pair → file → banner → revoke must be demonstrated in one warm
  session. If the service sleeps mid-demo, re-warm, re-pair, and
  re-file; do not splice a cold-start failure out of the video and
  claim a continuous live run.

## 6. Known deploy-time gaps (read before deploying)

1. **DB path is CWD-relative.** `VisitStore(os.environ.get("CLINICLINK_DB",
   "cliniclink.db"))` resolves relative to the process working directory,
   not `server.py`'s directory. If Render (or any launcher) starts the
   process from a different directory, the DB lands elsewhere. Verify
   where the file actually lands on first deploy, or set `CLINICLINK_DB`
   to an explicit path and record it.
2. **Pairing secret is per-process.** `PairingStore` generates a fresh
   32-byte secret at import. Two Render instances (if ever scaled)
   would not share tokens. Free tier runs one instance; do not scale
   without solving this.
3. **No keep-alive, no persistence guarantees.** Ephemeral disk + sleep
   + in-memory pairing = a demo, not a production clinic system. The
   submission must say exactly that (see README honest-limits card and
   PILOT_MEASUREMENT_PLAN.md — a plan, zero field data).
4. **Build fallback masks pip failure.** See §1. Harmless for stdlib,
   but a green build must not be quoted as "pip verified".
5. **No CI.** There is no `.github/workflows/` in the repo. Rulebook
   Gate E "CI checks pass" is therefore BLOCKED, not passed. A CI
   workflow (at minimum: run the 22 unittest tests on push) must be
   added before any release claims CI.
6. **No E2E.** No Playwright suite. The live checklist in §3 is the
   manual E2E until one exists.

## 7. Rollback

- **Rollback = redeploy the previous known-good commit from GitHub.**
  Record the previous SHA before each deploy. If the live service is
  broken, redeploy that SHA, then re-run §3 in full (a rollback is a
  restart: DB rows and pairing tokens are gone, re-seed and re-pair).
- **Data rollback is not applicable:** demo data is synthetic and
  ephemeral by design. There is nothing to restore, and nothing real
  to lose. Do not claim a backup exists.
- **If Render itself is unavailable or demands a card:** stop, mark
  the deploy BLOCKED with the exact reason, and do NOT fall back to
  Cloud Run (card) or to claiming a local URL as live. Paper-only
  fallbacks that were NOT attempted and must NOT be claimed as tried:
  Vercel Hobby, Cloudflare Workers free.

## 8. Ownership and next steps (in order, user steps marked)

1. (User) AgentFoundry signup + structuring-step verification — the
   eligibility gate. See `AGENTFOUNDRY_IMPORT_GUIDE.md`. Stop if a
   card is asked. Only the permitted wording in that guide may be
   used in the submission issue afterwards.
2. (User) Render free deploy (§2) + live checklist (§3).
3. (User) Re-record / re-check the demo video's live shot from the
   live URL (see `submission/DEMO_VIDEO_MANIFEST.md`).
4. (User) File the submission issue in `karlmehta/code-for-a-billion`
   (each submission is a public issue labelled `submission`), with
   honest AgentFoundry wording, size/severity numbers ONLY with a
   source cited at filing time, repo URL, live demo URL and/or video,
   and an honest Proven-impact statement (working prototype + live
   deployment + measured timing if any + PILOT_MEASUREMENT_PLAN.md as
   a plan with zero field data; explicitly no real clinic deployment
   and no invented field data). Save the issue URL — only then is
   ClinicLink "submitted".
5. **Do NOT double-submit.** Bharat Agentic-AI is the SAME Code for a
   Billion umbrella as this entry. ClinicLink IS the Bharat entry (if
   it fits the Agentic-AI theme). Do not file it a second time as a
   separate Bharat project.
