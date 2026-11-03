# ClinicLink — Demo Video Manifest

**Project:** ClinicLink — evening transcription → minute-in escalation
**Repo:** https://github.com/MSAbhishek22/cliniclink — commit `def70ad7`
  (at gate-file writing time)
**Rulebook:** ABHI_22 Global Project Quality Rulebook v1.0, §7.
**Status: BLOCKED (not live-recorded).** Read this file before quoting any
video link as a demo. The existing video is NOT a live-recorded demo,
and must not be presented as one.

## 1. Existing video — what it actually is

| Field | Value (verified from prior records, NOT re-verified by a live run here) |
|---|---|
| Narrated video (current submission link) | https://youtu.be/DElQR7QuOW0 (shown as 2:51 on YouTube) |
| Silent version (left untouched, NOT the submission link) | https://youtu.be/KhvpDVkbIgo (2:50) |
| Origin | Local UI footage (narrated version = same footage as the silent version + narration). The original silent file was NOT deleted or replaced. |
| Recorded from a live Render URL? | **NO.** No Render deployment exists, so no live URL existed to record from. The live shot in the video (DEMO_SCRIPT.md Shot 4) is **NOT verified as a real Render URL**. |
| Duration / target | ~2:50, within the 2–3 minute shot-list target in DEMO_SCRIPT.md. Duration alone does not make it live-recorded. |
| Synthetic-data labelling | Every household in the demo is captioned SYNTHETIC DATA in the UI and must remain so in any re-record. No real patient data, no diagnosis claim, anywhere. |

**Do NOT claim:** that https://youtu.be/DElQR7QuOW0 is "recorded from the
live demo", "live proof", or "the deployed app working". It is a
local-footage video with narration. Quoting it as live proof would be
manufactured evidence under Rulebook §7 and §11.

## 2. What the rulebook requires (and what is missing)

Mandatory order (Rulebook §7):
`Deploy → Verify Production → Freeze Release Commit → Record Demo from
Production URL → Review Video → Publish/Deliver Video → Attach Verified
Video URL`

| Step | Status |
|---|---|
| Deploy (Render free) | BLOCKED — pending user signup + deploy (§2 of the runbook; stop if a card is asked) |
| Verify Production (runbook §3 checklist) | BLOCKED — no live URL to verify |
| Freeze Release Commit | BLOCKED — no deployed SHA to freeze |
| Record Demo from Production URL | BLOCKED — this is the step that produces a compliant video |
| Review Video (factual accuracy, secret leakage) | BLOCKED — nothing live-recorded to review |
| Publish/Deliver Video | BLOCKED_AUTHORIZATION in rulebook terms for any NEW upload until the user approves visibility/metadata; the EXISTING narrated video's publish state is "uploaded, Unlisted, not live-recorded" — do not conflate the two |
| Attach Verified Video URL | BLOCKED — no live-recorded video URL exists |

## 3. Required re-record (after deploy — do not skip)

After the Render deploy is live and the runbook §3 checklist has passed
in full, in ONE warm session (no redeploy in between — pairing tokens
die on restart):

1. **Warm the service first.** Free tier sleeps after ~15 min idle;
   expect a ~60s cold start. Say so on camera if it is asleep; cut to
   the warm response. Do NOT fake a live response with a local
   screenshot.
2. **Re-record Shot 4 (live deployed URL responding) from the live URL:**
   open the deployed Render URL in a fresh browser tab, show `/health`
   responding (200, `synthetic_only: true`, `diagnosis: never`), then
   one filed record on the live service.
3. **Re-check every other shot against the live URL** (Phone pair →
   file → banner, Clinic summary + banner, revoke). If any shot in the
   existing video cannot be reproduced live, re-record that shot too —
   do not keep a local shot and label the video "live".
4. **Keep the honest-limits card** (DEMO_SCRIPT.md Shot 5): synthetic
   data only, no real clinic deployment yet, no diagnosis, pilot plan
   with zero field data. Any scripted timing comparison must use ONLY
   numbers actually measured on camera (visible stopwatch, same
   synthetic household, same fields) — no percentage improvement, no
   error-rate statistic.
5. **Fill in this manifest with real values, then publish:**
   - Production URL actually recorded from
   - Release version + deployed commit SHA actually recorded from
   - Recording date (UTC + IST)
   - Video duration, file location, and the VERIFIED published/unlisted
     video URL read back from the platform (never invented)
   - Reviewer note: factual accuracy checked, no secrets in any frame
     (no tokens, no codes, no credentials — the approval code shown
     during pairing in a demo is a throwaway demo code; if a real
     token ever appears in a frame, re-record without it)

## 4. If production code changes after recording

Rerun relevant QA and record a new demo. The video must not claim
features absent from the deployed release. The existing narrated video
must then be replaced as the submission link (or explicitly retired in
the submission issue) — do not leave two contradictory "submission
videos" in circulation without saying which one is current.

## 5. Manifest fields (to be completed ONLY after a live re-record)

| Field | Value |
|---|---|
| Production URL recorded from | null — no live URL yet |
| Release version recorded from | null |
| Deployed commit SHA recorded from | null |
| Recording date (UTC / IST) | null |
| Video file (local path, duration) | null — existing file is local-footage only, not the live-recorded file |
| Published / verified video URL | null for the live-recorded video (existing narrated URL above is NOT this field) |
| Review status | NOT REVIEWED (live-recorded video does not exist) |

**Bottom line:** Until §3 is done, `DEMO_VIDEO_RECORDED_FROM_LIVE =
BLOCKED` and `VIDEO_PUBLISHED_AND_URL_VERIFIED = BLOCKED` for the
live-recorded video. The existing narrated video may be linked as a
local demo with that label, and only with that label.
