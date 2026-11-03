# AgentFoundry import guide — honest version

**Status: NOT DONE. This local build alone does NOT satisfy
"Built using AgentFoundry".** Do not write that line in the submission
until the steps below have actually been done by the user, in his own
browser, and can be described truthfully. This guide tells him exactly
what to do and what to write — and what not to claim.

## What AgentFoundry is, in this entry's terms

Per the official Code for a Billion pages, every participant gets 1M
smart-code tokens free on AgentFoundry.me, and the entry must be built
in the AgentFoundry IDE. The AgentFoundry step for ClinicLink is one
specific thing, not "the whole app was written there":

> An agent step inside AgentFoundry that takes a filed visit report
> (worker, household, visit type, note, danger-sign checklist) and
> produces **the same record shape** this prototype produces —
> including the rule that escalation is `escalate_per_protocol` if and
> only if a danger sign is ticked, and `routine` otherwise, with
> free-text notes stored verbatim and never auto-diagnosed.

The local prototype proves the record shape, the escalation rule, the
pairing gate, and the dashboard with deterministic rules only. It calls
no model API. The AgentFoundry step is the LLM structuring producing
that same shape — with the checklist rule enforced in the prompt and
in validation, not left to the model's judgement.

## Step-by-step (user, in his own browser)

1. **Sign up at AgentFoundry.me, create the ClinicLink project.**
   STOP AT ONCE if signup asks for a card. Official pages say "no
   credit card" and 1M tokens free, but signup was never tested by
   the agent (no accounts were created). A card demand is an instant
   NO-GO for this step — report it, do not enter card details.
2. **Import this `cliniclink/` code into the AgentFoundry project.**
   Keep it as a separate module — do NOT import or push Abhiverse
   itself. The entry released to the Code for India org is ClinicLink
   only, with attribution, per the hackathon's IP terms.
3. **Build the agent structuring step in the IDE.** Suggested prompt
   skeleton (adapt to the IDE's actual agent format — do not claim a
   format you did not use):
   - Input: the filed report fields exactly as the phone sends them.
   - Output: the same record shape (`worker_id`, `household`,
     `visit_type`, `note`, `danger_signs`, `escalation`, `synthetic`).
   - Hard rule, in the prompt AND in post-validation: escalation is
     `escalate_per_protocol` only if a listed danger sign is ticked;
     free-text notes must never change escalation, never be treated
     as a diagnosis, and must be copied verbatim.
   - Reject unknown danger signs and bad visit types, exactly as
     `cliniclink/models.py` does.
4. **Run it against the demo cases and compare.** Use the same cases
   the tests cover: routine visit (no tick → routine), fever ticked
   → escalate, scary-sounding note with no tick → still routine,
   unknown sign → rejected. The AgentFoundry output must match the
   local output on every case before you claim the step works.
   If the model ever escalates from note text alone, that is a
   failure of the step, not a feature — fix the prompt/validation
   and re-run; do not ship it.
5. **Screenshot / save evidence.** Keep the AgentFoundry project view
   and at least one agent run showing the input → record output.
   These are for your own verification and for the submission issue's
   honest description — do not fabricate a run you did not do.
6. **Wire or document the boundary.** If the IDE project cannot
   directly serve the demo UI, say so: the demo UI + pairing + SQLite
   store remain the local/Render deployment, and AgentFoundry is the
   structuring agent step that was verified to produce the same
   record shape. A documented boundary beats an invented integration.

## What to write in the submission issue (only after doing it)

Write, in your own words, something like:

> "Built locally in Python (stdlib only), then imported into
> AgentFoundry, where the agent structuring step was verified to
> produce the same record shape and escalation rule as the local
> prototype on [the demo cases you actually ran]. The demo UI,
> pairing gate, and local store run from [repo + Render link]."

If any part of that sentence is not yet true, cut that part out and
say what is true instead. Judges penalise a discovered overclaim
more than an admitted gap — and the gap is already disclosed in the
README's honest-limits card.

## What NOT to claim

- Do not claim the whole app was "built in AgentFoundry" if only the
  structuring step was verified there.
- Do not claim an AgentFoundry deployment, token usage, or model
  name you did not actually use.
- Do not paste any AgentFoundry token, key, or credential anywhere —
  not in the repo, not in the issue, not in chat.
- Do not use Cloud Run for deployment — it needs a card. Render free
  tier is the deploy path on paper (see SUBMISSION_CHECKLIST.md).
