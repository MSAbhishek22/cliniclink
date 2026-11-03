# ClinicLink — Design Constitution

**Project:** ClinicLink — evening transcription → minute-in escalation
**Entry:** Code for a Billion — Bharat Agentic-AI Hackathon 2026 (Code for India)
**Repo:** https://github.com/MSAbhishek22/cliniclink — commit `def70ad7` (at gate-file writing time)
**Status of this document:** Written from the ACTUAL shipped UI (`static/index.html`,
`server.py`, `cliniclink/*.py`) on 3 Nov 2026. It describes what the product IS,
not what a future redesign might be. Anything not yet built is marked PLANNED.
**Rulebook:** ABHI_22 Global Project Quality Rulebook v1.0, §1.2.

> **Hard boundaries (never soften these in copy, UI, or video):**
> - Synthetic data only. No real patient data, ever.
> - Never a diagnosis, never treatment advice. The only escalation output is
>   the prompt `escalate per protocol`, produced ONLY by a danger-sign
>   checklist tick. Free-text notes are stored verbatim and never escalate.
> - Records stay on the clinic laptop (local SQLite). No central health cloud,
>   no subscription, no trackers.

## 1. Product personality and emotional tone

- **Personality:** A paper register that learned to travel. Calm, plain, and
  trustworthy — the opposite of a loud health-tech dashboard. The worker is
  the hero; the clinic laptop is the quiet host.
- **Tone:** Factual, short, observational. Danger-sign wording is
  observational ("worker saw / household reported"), never diagnostic.
  Copy says what happened and what to do next ("follow the clinic's own
  protocol"), never what the condition is.
- **Story in one line:** "Evening transcription → minute-in escalation."
  Not "a better form". The differentiator is TIME: hours (paper, evening
  re-typing) → the same minute (phone filing, dashboard banner).

## 2. Target user, environment, context of use

- **Primary user:** A frontline health worker in the field, filing on a phone
  (small screen, large tap targets, one hand, possibly poor connectivity
  in the real world — the demo itself runs on one host and does NOT claim
  offline sync; offline-first is the clinic model, not a tested demo feature).
- **Secondary user:** Clinic staff on a laptop dashboard, scanning today's
  summary cards and the red escalation banner at a glance.
- **Context:** Village lanes, paper registers, a clinic laptop that was
  never the problem — the distance was. No accounts, no same-Wi-Fi
  assumption, no subscription is assumed for the clinic model; the demo
  enforces trust with approval pairing instead.

## 3. Visual metaphor / central design idea

**The register, split in two and joined by a minute.**
The Phone tab is the field page of the register; the Clinic tab is the
clinic page of the same register. A single visit card travels from one
to the other, and a danger-sign tick turns that card's edge and banner
red. Nothing else in the UI is decorative: every colour change means
"this household needs protocol follow-up".

## 4. Colour palette (semantic roles, actual values from `static/index.html`)

| Role | Value | Where it is used |
|---|---|---|
| Clinic green (trust, header, primary action) | `#123c2e` | Header background, tab selected state, primary buttons, borders |
| Paper / warm off-white (background) | `#f6f5f1` | Page background |
| Card white | `#fff` | Story, cards, visit entries |
| Border grey | `#ddd` (cards), `#aaa` (inputs) | Card/input borders |
| Warning yellow (badge, active step) | `#ffd23f` | `SYNTHETIC DATA ONLY` badge, active pair step |
| Escalation red (only meaning: protocol flag) | `#a00` | Escalation banner, escalated visit border, `escalate` pill, danger button |
| Success green (paired / routine) | `#d8ead9` | Completed pair step, `routine` pill |
| Summary green tint | `#eef3ef` | Summary stat cards |
| Muted text | `#555` (small), `#444` (footer) | Secondary text |

Red is NEVER used for decoration, branding, or generic emphasis. If it is
red, a danger sign was ticked. Yellow is NEVER a warning about a fault —
it is the synthetic-data label and the active-step marker only.

## 5. Typography and type hierarchy

- **Typeface:** System stack only — `system-ui, -apple-system, sans-serif`.
  No webfont, no CDN (tests assert no external CDN assets). This is a
  deliberate choice for a low-bandwidth clinic context, not an omission.
- **Hierarchy (actual):**
  - H1 `ClinicLink` 1.35em (1.15em ≤480px) in the header, with the story
    line directly under it.
  - H2 card titles 1.1em (`1. Pair the phone…`, `2. File a visit…`,
    `Clinic laptop — today's summary`).
  - H3 `Today's visits (newest first)`.
  - Labels 600 weight, above their inputs. Body line-height 1.45.
  - Stat numbers 1.6em bold (1.3em ≤480px).
- **Rule:** No other type scale exists in the product. Do not add a
  display font without updating this constitution and the registry.

## 6. Layout grid, spacing, composition

- **Single column, max-width 760px, centred** (`.wrap`), 1em side padding,
  2em bottom padding. No sidebar, no multi-column dashboard grid.
- **Composition order on every load:** header (title + synthetic badge +
  story line) → story card (3-step gap narrative) → Phone/Clinic tabs →
  escalation banner (hidden until an escalation exists) → Phone view →
  Clinic view (hidden until its tab is chosen) → footer (honest limits).
- **Cards:** white, 1px `#ddd` border, 10px radius, 1em padding, 1em vertical
  margin. Stats: 3-column grid (`.stats`), each stat centred on `#eef3ef`.
- **Spacing system:** 0.5–1em increments only (margins/padding in the
  stylesheet are 0.2–1em). No arbitrary pixel values outside the stylesheet.

## 7. Navigation and information architecture

- **Two tabs only**, `role="tablist"`, with `aria-selected` toggled by
  `switchView()`:
  - `📱 Phone — file from the field` (default)
  - `💻 Clinic laptop — dashboard` (switching to it auto-refreshes summary)
- **No other routes.** `/` serves the single page; every other user
  journey is a section inside it (pair → file → dashboard). There is no
  settings page, profile page, search page, or separate admin route.
- **Pair stepper (display only, NOT a control):** `1 · Request → 2 ·
  Approve → 3 · Paired ✓`, states `active` (yellow) / `done` (green).
  It shows progress; it is never clickable. See `qa/INTERACTION_INVENTORY.md`.

## 8. Component behaviour and interaction patterns

- **Buttons:** Primary = green `#123c2e` background, white text, 8px radius.
  Secondary = white background, green text/border. Danger = red `#a00`
  (reserved; no danger button is currently rendered — the class exists in
  CSS but is unused, see inventory note).
- **Inputs:** Full-width, 0.7em padding, 1em font, 1px `#aaa` border,
  8px radius. Labels sit above inputs and wrap them. Select for visit
  type; textarea (3 rows) for notes; checkboxes for danger signs, rendered
  dynamically per visit type.
- **Danger-sign checklist:** Rendered by `renderSigns()` on visit-type
  change. Pregnancy 6 signs, newborn 6, general 5. For `follow_up` and
  `immunisation_reminder` the UI falls back to the general list (the
  server catalogue has no group for those types; validation checks sign
  membership against the flat catalogue, so a general sign on a follow-up
  visit is valid — the UI does not explain this fallback; see inventory).
- **Escalation banner:** `role="alert"`, hidden (`display:none`) until a
  filed visit escalates or the summary contains escalations, then shown
  in red with the household(s) and ticked signs named.
- **Feedback pattern (actual, not aspirational):** Status lines
  (`#pairStatus`, `#fileStatus`) are plain text updated after each fetch.
  There is NO loading spinner, NO disabled-during-fetch state, and NO
  duplicate-click guard — see §11 and the inventory. Do not describe
  these as present.

## 9. Motion language, transitions, micro-interactions, loading states

- **Current motion: none.** There are no CSS transitions, animations,
  hover transforms, or skeleton loaders in `static/index.html`.
  Buttons change only via the browser default cursor; tab selection
  changes background colour instantly; the banner appears instantly.
- **Rule going forward:** Any motion added must communicate
  cause-and-effect (e.g. filed → banner appears) or progress (e.g.
  submitting state), must be restrained, and must never delay filing.
  Loading states, if added, must be the FIRST motion work, before any
  decorative animation.

## 10. 3D concept — PLANNED ONLY (does NOT exist in the shipped UI)

> **Status: PLANNED. No 3D code ships in this build. Do not claim a 3D
> feature, screenshot, or video frame for ClinicLink until it is built
> and tested.**

- **Concept (meaningful, not decorative): "The minute the record travels."**
  A depth-layered journey, left-to-right and foreground-to-background:
  - **Foreground — the field:** the phone card, where the worker ticks a
    danger sign.
  - **Middle lane — the minute:** the visit card travels along a shallow
    depth lane from phone to clinic. The card is routine (green edge)
    unless a tick is present, in which case its edge and the destination
    banner turn red as it arrives.
  - **Background — the clinic:** the laptop dashboard, where the card
    lands in today's list and the red banner rises.
  - The user can drag/scrub the journey, or step through it with
    keyboard controls (Field → Travelling → Clinic). The interaction
    teaches the product's only differentiator (time), not a generic
    spinning object.
- **Technology (proposed, not chosen):** CSS 3D transforms only — no
  WebGL/Three.js dependency for a product whose real UI is stdlib HTML.
  If CSS 3D cannot carry the journey legibly, the fallback IS the
  product: the existing 3-step story list.
- **Fallback:** A static 2D flow diagram identical in content to the
  story `<ol>` (Morning → Same minute → Danger sign ticked?). The 3D
  layer must never be the only way to understand the journey.
- **Reduced motion:** With `prefers-reduced-motion`, no card travels.
  The journey is shown as the static diagram only.
- **Mobile / low power:** The 3D layer loads lazily, only on the story
  section, and is disabled on narrow viewports if it hurts legibility.
  The filing workflow must work identically with the layer absent.
- **Gate:** 3D_EXPERIENCE = FAIL until this is built, tested on desktop
  + mobile viewports, and given a keyboard alternative. An exception
  needs explicit user approval under Rulebook §3 — it has not been
  requested or granted.

## 11. Responsive behaviour

- **Desktop:** 760px centred column, 3-column stats grid.
- **Tablet:** Same column (no tablet breakpoint exists); content reflows
  by max-width, not by a tablet layout.
- **Mobile (≤480px media query):** Header H1 1.15em, stat numbers 1.3em.
  The stats grid STAYS 3 columns at 480px (the media query restates
  `1fr 1fr 1fr`), so three narrow columns on a small phone — recorded
  here as a known responsive weakness, not hidden.
- **Untested in a real browser:** No Playwright/E2E suite, no Lighthouse
  run, no device testing is recorded for this build. Responsive and
  accessibility status is therefore PARTIAL/UNTESTED, not PASS. See the
  gate card.

## 12. Accessibility and reduced-motion behaviour

- **Present:** `lang="en"`, viewport meta, labels wrapping inputs,
  dynamically generated checkboxes inside `<label>` elements, tablist
  with `aria-selected`, banner with `role="alert"`, 1.45 line-height,
  system fonts (no tiny webfont text).
- **Missing / partial:** No custom `:focus-visible` styling (browser
  default only); danger-sign checkboxes have no `<fieldset>`/`<legend>`;
  the pair stepper has no ARIA progress semantics (it is spans, not a
  progressbar); no `prefers-reduced-motion` handling exists yet (there
  is currently no motion to reduce — the 3D plan in §10 must add it);
  colour is the sole carrier of escalation state in pills/banners
  (red vs green) — text labels (`ESCALATE PER PROTOCOL` / `routine`)
  are always present alongside colour, which mitigates but does not
  remove the check.
- **Rule:** Any new control must have a label, a visible focus state,
  and a text label alongside any colour-only meaning.

## 13. Design references — BLOCKED in this pass (not invented)

No five-reference design research pass was performed for this gate file,
and no reference site is claimed as inspected here. The references
below are the project's own prior sources (hackathon rules and prior
work), NOT design references:

- Code for a Billion official pages (event rules, judging) — cited in
  README.md, not a design inspection.
- Abhiverse (the user's own project) — the pairing concept's origin,
  not a UI reference for ClinicLink.

**Before any redesign or any claim of Gate A completion, a real
five-reference pass (Rulebook §1.1: two same-category, one interaction/
motion, one typography/hierarchy, one 3D/spatial) must be done with
URL, date, what was inspected, what to learn, what NOT to copy, and
translation into this identity — or the blocker must stay labelled
BLOCKED.** Do not backfill this section with invented URLs.

## 14. Distinctness vs the three most recent projects (registry comparison)

Compared with the three most recent ABHI_22 projects at gate-file time:

| Project | Identity | ClinicLink difference |
|---|---|---|
| CageCheck (Vultr) | Paper/ink/stamp, serif + mono receipts, single 720px column, stamp verdict | Different story and palette (clinic green/yellow/red, system type, tabs + banner), same single-column + card pattern — layout pattern overlaps, concept does not |
| ChatBoss (Codex × TwitchCon) | Dark game gradient, animated HP bars, event feed, leaderboard | Opposite in every respect: light paper background, calm clinic story, no game chrome, no gradient |
| Spec Ghost (Kiroween) | Dark haunted house, candlelight amber, rooms/ghosts | Opposite palette and mood: light, clinical, daylight; ghosts/rooms metaphor absent |

**Verdict: UI_DISTINCTIVENESS = PASS with a noted layout-pattern overlap.**
ClinicLink is recognisably different in concept, palette, typography
(system vs serif/mono vs game), navigation (Phone/Clinic tabs), and
signature interaction (tick → red banner). Its single-column + card
layout pattern is shared with CageCheck — that pattern is a layout
choice, not a copied visual identity, but a future redesign should
differentiate layout as well as palette if the registry comparison is
to stay PASS.

## 15. What must NOT change without updating this document

Palette roles (especially: red = ticked danger sign only), the
synthetic-only badge on every screen, the tick-only escalation rule,
the Phone/Clinic tab structure, and the "never a diagnosis" footer.
Any change to these is a product change, not a cosmetic tweak.
