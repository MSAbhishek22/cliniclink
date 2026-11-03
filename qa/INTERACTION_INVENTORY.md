# ClinicLink — Interaction Inventory

**Project:** ClinicLink — evening transcription → minute-in escalation
**UI under test:** `static/index.html` (single page, Phone + Clinic tabs) served by
`server.py` (stdlib `ThreadingHTTPServer`, binds `0.0.0.0`, `$PORT` → `CLINICLINK_PORT` → `8000`)
**Repo:** https://github.com/MSAbhishek22/cliniclink — commit `def70ad7`
**Test evidence:** `python3 -m unittest discover -s tests` — **22/22 PASS** on Linux,
re-run 3 Nov 2026 during gate-file writing (tests listed at the end).
**Rulebook:** ABHI_22 Global Project Quality Rulebook v1.0, §4.1.
**Status rule:** PASS = control works as described and is covered by a test or a
verified local run. FAIL = control is visible but does not work as described,
or its behaviour is unguarded in a way the rulebook forbids. BLOCKED = cannot
be verified here (needs live deployment / real browser / user step).
**Scope note:** This inventory covers the shipped UI and API. It is NOT a
browser E2E result — no Playwright suite exists (see §4). DOM click behaviour
below is read from the shipped JavaScript and the API tests, not from a
recorded browser session. That limit is stated, not hidden.

> **Global rules that apply to every row:**
> - Synthetic data only, on every screen (badge `SYNTHETIC DATA ONLY`).
> - Escalation = `escalate_per_protocol` ONLY if a danger sign is ticked.
>   Note text never escalates, never diagnoses.
> - Pairing tokens are in-memory only, per-process secret, 600s approval-code
>   expiry. A restart/redeploy invalidates every token.
> - No control in this inventory is a link to an external site, a download,
>   an upload, a search/filter, pagination, or an auth login form — none of
>   those exist in the product.

## A. Visible UI controls — Phone tab (default view)

| # | Control (page / component) | User action | Expected behaviour | Actual behaviour (code) | Validation / error | Test evidence | Status |
|---|---|---|---|---|---|---|---|
| A1 | Tab: "📱 Phone — file from the field" (`#tabPhone`, `role=tablist`) | Click | Show Phone view, hide Clinic view, `aria-selected=true` | `switchView('phone')` toggles `hidden` + `aria-selected` | None needed | `test_homepage_is_demo_ready` (tab text present) | PASS |
| A2 | Tab: "💻 Clinic laptop — dashboard" (`#tabClinic`) | Click | Show Clinic view, hide Phone view, auto-refresh summary | `switchView('clinic')` toggles + calls `refresh()` | Summary fetch failure would leave stale "–" stats (no error UI) — see §4 | Homepage test (tab text present); API summary test | PASS* (auto-refresh error UI missing — minor, see §4) |
| A3 | Pair stepper display (`#pairSteps`: 1·Request / 2·Approve / 3·Paired ✓) | None — display only | Show pairing progress: active (yellow) / done (green) | Spans only, class changed by `setStep(n)`; NOT clickable | None | Manual code read; no dedicated test | PASS (indicator, not a control — must never be presented as clickable) |
| A4 | Device id input (`#device`, default `DEMO-PHONE-01`) | Type device id | Value sent as `device_id` on pair request | Sent verbatim in `POST /api/pair/request` body | Empty/blank → API 400 `device_id is required`; UI shows the returned JSON, not a friendly error | `test_no_token_before_approval`, pair-flow tests | PASS |
| A5 | Button "Request pairing" (`pairRequest()`) | Click | Mint a 6-digit approval code, fill code input, step → 2 | `POST /api/pair/request`; on `approval_code`, fills `#code`, `setStep(2)`; status line shows the code in plain text | Empty device → 400 shown as JSON in status line | Pair-flow tests | PASS (code-in-plain-text is a DEMO-ONLY limitation, §4) |
| A6 | Approval code input (`#code`, placeholder "6-digit code from step 1") | Type / auto-filled 6-digit code | Value sent as `approval_code` on approve | Sent verbatim in `POST /api/pair/approve` | Wrong code → API 400, UI "Approval failed: {json}"; expired (>600s) → API 400 `approval code expired`, pending deleted | `test_wrong_code_does_not_pair`, `test_approve_without_request_fails`, `test_correct_code_pairs_and_revocation_kills_it` | PASS |
| A7 | Button "Approve with code" (`pairApprove()`) | Click | Mint pairing token, step → 3, filing enabled | Token stored in JS `token`; status "Paired ✓"; `setStep(3)` | No pending request → 400; wrong/expired code → 400 (above); failure leaves token empty | Pair-flow tests | PASS |
| A8 | Button "Revoke pairing" (`revokePairing()`) | Click | Revoke token, step → 1, filing blocked until re-approved | `POST /api/pair/revoke`; on `revoked:true` clears token, `setStep(1)`; status explains filing blocked | No token → UI guard "Nothing paired to revoke." (no API call); unknown token via API → `revoked:false`, 200 (not an error) | `test_correct_code_pairs_and_revocation_kills_it`, `test_revoked_token_cannot_file_via_api` | PASS |
| A9 | Worker id input (`#worker`, default `DEMO-WORKER-01`) | Type worker id | Sent as `worker_id` on filing | Sent verbatim in `POST /api/visits` | Blank → API 400 `worker_id is required`; UI shows "Failed (400)" | `test_missing_household_rejected` (household analogue), model validation tests | PASS |
| A10 | Household input (`#household`, default `Synthetic Household 12`) | Type household | Sent as `household` on filing | Sent verbatim | Blank → API 400 `household is required` | `test_missing_household_rejected` | PASS |
| A11 | Visit type select (`#vtype`: pregnancy / newborn / general / follow_up / immunisation_reminder) | Change | Re-render danger-sign checklist for that type | `renderSigns()` on change; pregnancy→6 signs, newborn→6, general→5, follow_up/immunisation_reminder→general list (fallback, NOT explained in UI — §4) | Bad type via API → 400 `visit_type must be one of …`; UI select cannot produce a bad type | Model validation tests (`test_bad_visit_type_rejected`) | PASS (fallback unexplained — minor, §4) |
| A12 | Note textarea (`#note`, 3 rows, default "Routine check-in, synthetic demo.") | Type note | Stored verbatim (whitespace collapsed), NEVER escalates on its own | `structure_note` collapses whitespace, stores verbatim; escalation ignores note text | >2000 chars → API 400 `note must be at most 2000 characters` | `test_note_text_never_creates_escalation` (scary note, no tick → routine) | PASS |
| A13 | Danger-sign checkboxes (`.sign`, dynamic per visit type) | Tick/untick signs | Tick is the ONLY thing that can produce `escalate_per_protocol` | Checked values sent as `danger_signs` array; server validates membership in flat catalogue | Unknown sign → API 400 `unknown danger_signs: […]`; no tick → `routine` | `test_routine_when_no_danger_sign`, `test_any_danger_sign_escalates`, `test_unknown_danger_sign_rejected`, `test_every_catalogued_sign_is_valid` | PASS |
| A14 | Button "File report" (`fileVisit()`) | Click | File visit (201), show escalation, refresh clinic view, show banner if escalated | `POST /api/visits` with `X-Pairing-Token`; 201 → status "Filed (SYNTHETIC DATA). Escalation: …", banner if escalated, `refresh()` | No token → 401 `pairing required`; validation → 400; UI shows "Failed (status): {json}"; NO loading/disabled state, NO duplicate-click guard — double-click files twice (§4, FAIL item) | `test_full_flow_pair_then_file_then_summary`, `test_visit_requires_pairing` | FAIL (duplicate-click guard missing; filing itself works) |
| A15 | Button "Load synthetic demo records" — Phone card (`seed()`) | Click | Seed 3 labelled synthetic records, refresh | `POST /api/seed` (no auth); status "Seeded 3 synthetic records."; `refresh()` | None; NO confirmation, NO dedupe — repeated clicks duplicate the 3 seed records (§4) | `test_seed_endpoint_loads_synthetic_records` (first load only) | FAIL (unguarded repeat-seed; seeding itself works) |
| A16 | Status lines `#pairStatus`, `#fileStatus` (text, not controls) | Read | Show pairing/filing outcome in plain text | Updated after every fetch; errors shown as raw JSON | Raw-JSON error text is unfriendly but truthful | Pair/file flow tests (API side) | PASS (display only) |

## B. Visible UI controls — Clinic tab

| # | Control | User action | Expected behaviour | Actual behaviour | Validation / error | Test evidence | Status |
|---|---|---|---|---|---|---|---|
| B1 | Summary stat cards: visits filed today / escalations flagged / households seen today (`#statVisits`, `#statEsc`, `#statHouse`) | Read (auto-filled on tab switch / refresh) | Show today's counts from `/api/summary` | `refresh()` sets counts; households card shows count of distinct households (list itself is in summary JSON, not rendered as a list in the UI) | Summary fetch failure leaves "–" with no error UI (§4) | `test_add_and_summary_counts_escalations`, `test_summary_lists_escalated_visits_for_banner` | PASS |
| B2 | Button "Refresh summary + visits" (`refresh()`) | Click | Re-fetch summary + visits, re-render list + banner | Fetches `/api/summary` + `/api/visits`, renders visit cards, shows banner if escalations exist | Fetch failure → unhandled promise path, stale list (no error UI) | Summary/visits API tests | PASS* (error UI missing — minor, §4) |
| B3 | Button "Load synthetic demo records" — Clinic card (`seed()`, same handler as A15) | Click | Same as A15 | Same as A15 | Same as A15 (no confirmation, no dedupe) | Seed test (first load only) | FAIL (same unguarded repeat-seed as A15) |
| B4 | Today's visits list (`#visitList`, newest first) | Read | Each visit: household, visit type, escalation pill, SYNTHETIC pill, worker, note, danger signs; escalated visits get red 2px border | Rendered from `/api/visits`; pill `escalate` (red) vs `routine` (green); empty state "No visits yet today." | None | Visits API tests; homepage test | PASS |
| B5 | Escalation banner (`#escalationBanner`, `role="alert"`, hidden until escalation) | Read | Show red banner naming escalated household(s) + ticked signs, "follow clinic protocol", "never a diagnosis" | Shown by `showBanner()` on filed escalation and on refresh when `escalated_visits` non-empty; hidden otherwise | Banner text is built from API data; no dismissal control exists (by design — banner is unmissable) | Banner-data test (`test_summary_lists_escalated_visits_for_banner`) | PASS |
| B6 | Hidden debug element `<pre id="out">` (`display:none`) | None — never shown | (No user-facing behaviour) | Filled with `{summary, visits}` JSON on every refresh, but CSS hides it and NO control ever reveals it | None | None (not covered by tests) | FAIL (dead code, not a dead button: remove before release, or wire a real "view raw data" control with a label) |

## C. API routes (all JSON, stdlib server, no external calls)

| Route | Auth | Behaviour | Validation / error | Test evidence | Status |
|---|---|---|---|---|---|
| `GET /` , `GET /index.html` | — | Serve `static/index.html` | — | `test_homepage_is_demo_ready` | PASS |
| `GET /health` | — | `{"status":"ok","service":"cliniclink","version":"0.1.0","synthetic_only":true,"diagnosis":"never"}` | — | `test_health_endpoint` | PASS |
| `GET /api/danger-signs` | — | Full catalogue grouped pregnancy/newborn/general | — | Catalogue validity test | PASS |
| `GET /api/visits` | — (unauthenticated by design in demo) | All visits, newest first | — | Visits API tests | PASS (demo-only auth gap, §4) |
| `GET /api/summary` | — (unauthenticated by design in demo) | Today's counts, escalated visits, households, follow-up note (never a diagnosis) | — | Summary tests | PASS (demo-only auth gap, §4) |
| `POST /api/pair/request` | — | `{"device_id"}` → 6-digit `approval_code`, `expires_in_seconds: 600` | Blank device → 400 `device_id is required` | Pair tests | PASS |
| `POST /api/pair/approve` | — | Matching unexpired code → `pairing_token` (HMAC, per-process secret) | No pending → 400; expired → 400 `approval code expired` + pending deleted; wrong code → 400 (constant-time compare) | Pair tests | PASS |
| `POST /api/pair/revoke` | Body `pairing_token` | Revoke token → `{"revoked": true/false}` | Unknown token → `revoked:false`, 200 (not an error — honest, not a bug) | Revocation tests | PASS |
| `POST /api/visits` | Header `X-Pairing-Token` (required) | Validate + structure + store → 201 record with `escalation` | No/invalid/revoked token → 401 `pairing required`; validation → 400 (worker/household/type/note/signs); malformed JSON body is swallowed to `{}` by `_read_json` then fails validation (no JSON-syntax error surfaced — §4) | Full-flow, 401, validation tests | PASS |
| `POST /api/seed` | — (unauthenticated by design in demo) | File the 3 `SYNTHETIC_SEED` records → `{"seeded": 3, "visits": […]}` | None; repeat calls duplicate records | Seed test (first load only) | PASS (demo-only auth/dedupe gap, §4) |
| Any other path | — | 404 `{"error": "not found"}` (GET and POST) | — | Implicit (no dedicated test) | PASS |

## D. Dead, untested, or unguarded controls — the honest list

These are the items that keep `ALL_VISIBLE_CONTROLS` from being PASS.
Nothing here is hidden; each item names the fix or the release decision.

1. **FAIL — No duplicate-click / loading guard (A14, A15, B3).**
   No button disables itself or shows a loading state during a fetch.
   Double-clicking "File report" files two records; double-clicking
   "Load synthetic demo records" seeds duplicates. Rulebook §4.3
   (repeated-click behaviour) is not met. Fix: disable on submit +
   in-flight flag, or dedupe seed by household+date. Until fixed, the
   demo must be filmed in single clicks, and the fix must land before
   any release claims "controls tested".
2. **FAIL — Hidden debug element (B6).** `<pre id="out">` is filled on
   every refresh but `display:none` and unreachable. It is not a visible
   dead button, but it is dead code in the release UI. Fix: delete it,
   or add a labelled "View raw summary JSON" control that reveals it.
3. **FAIL — No real-browser E2E.** Tests are unittest API + HTML-string
   checks (`test_homepage_is_demo_ready` asserts story text, tabs,
   banner data, synthetic labels, no CDN — it does not click anything
   in a browser). No Playwright suite, no recorded DOM-click session.
   Every PASS above for a DOM control is therefore "API + code-read",
   not "browser-verified". A Playwright pass over pair → file → banner
   → revoke is required before ALL_VISIBLE_CONTROLS can be PASS.
4. **PASS* — Missing error UI on summary/refresh (A2, B2).** If
   `/api/summary` or `/api/visits` fails, stats stay "–" and the list
   stays stale with no error message. Minor (demo path is local), but
   it violates Rulebook §4.2 (recoverable error state). Fix: an error
   line in the Clinic card.
5. **PASS* — Unexplained checklist fallback (A11).** `follow_up` and
   `immunisation_reminder` show the general checklist with no label
   explaining the fallback. Behaviour is valid (server accepts those
   signs), but the UI does not say so. Fix: a one-line note under the
   checklist for those two types.
6. **Limitation, not a control failure — demo-only auth gaps.**
   `GET /api/visits`, `GET /api/summary`, and `POST /api/seed` need no
   token. Anyone with the demo URL can list visits and seed records.
   This is acceptable for a labelled synthetic demo, and UNACCEPTABLE
   to present as production hardening. The submission must say so.
   (Filing itself is correctly gated: 401 without a token.)
7. **Limitation, not a control failure — approval code in plain text (A5).**
   The approval code is shown in `#pairStatus` and auto-filled into the
   code input, i.e. visible to the "phone" side. That models the clinic
   approving in the same demo session; in a real deployment the code
   must travel clinic-side only. Demo-only, must be stated.
8. **Limitation — malformed JSON (C, `POST /api/visits`).**
   `_read_json` swallows `JSONDecodeError`/`UnicodeDecodeError` to `{}`,
   so a malformed body surfaces as a validation 400, not a JSON error.
   Behaviour is safe (no record is filed), but the error message does
   not name the real problem. Fix: return 400 `invalid JSON` on decode
   failure.
9. **Limitation — pairing is per-process, not persisted (§C).**
   Tokens and pending codes live in `PairingStore` memory with a
   per-process secret. Restart/redeploy invalidates every token and
   every pending code. The live verification MUST therefore run
   pair → file → banner → revoke in one warm session with no redeploy
   in between (see `deployment/DEPLOYMENT_RUNBOOK.md`).
10. **Not a control — CSS classes with no rendered element.**
    `button.danger` exists in the stylesheet but no danger button is
    rendered. Harmless, but a release cleanup item: either use it for a
    clearly-labelled destructive action or delete the class.

## E. Test evidence (re-run for this inventory)

```
python3 -m unittest discover -s tests
Ran 22 tests in 1.084s — OK (Linux, 3 Nov 2026, gate-file writing)
```

Test names (22): routine when no danger sign; any danger sign escalates;
note text never creates escalation; unknown danger sign rejected; missing
household rejected; bad visit type rejected; every catalogued sign is
valid; no token before approval; wrong code does not pair; correct code
pairs and revocation kills it; approve without request fails; add and
summary counts escalations; records are flagged synthetic; health
endpoint; visit requires pairing; full flow pair → file → summary; seed
endpoint loads synthetic records; homepage is demo ready; revoked token
cannot file via API; summary lists escalated visits for banner; Render
YAML is free and port-aware; no secrets or real data in repo files.

**Coverage gaps (honest):** No browser DOM-click test, no mobile-viewport
test, no cold-start test, no repeat-click test, no malformed-JSON test,
no expired-code timing test (600s is a constant, not a time-mocked
test), no test for the follow_up/immunisation checklist fallback, no CI
run (no `.github/workflows/` in the repo). These gaps are why §D exists.

## F. Inventory verdict

- Visible controls inventoried: 16 Phone (A1–A16) + 6 Clinic (B1–B6, of
  which B6 is hidden dead code) + 11 API routes.
- PASS: all core journeys (pair → approve → file → banner → summary →
  revoke) work as described and are API-tested.
- FAIL items: duplicate-click guard, hidden debug element, no real-browser
  E2E (see §D items 1–3).
- **ALL_VISIBLE_CONTROLS = FAIL** until §D items 1–3 are fixed and a
  browser E2E pass is recorded. The product is usable and demo-able;
  it is not rulebook-clean. Do not report this inventory as PASS.
