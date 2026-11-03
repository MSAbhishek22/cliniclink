# ClinicLink demo video — 2–3 minute shot list

Record only after the Render deploy is live (see SUBMISSION_CHECKLIST.md).
Every on-screen household must carry the caption **"Synthetic data"**.
Total target: under 3 minutes. No real patient data, no clinic, no
diagnosis claim anywhere in the video. The story to land, in one line:
**evening transcription → minute-in escalation** — not "a better form".

## Shot 1 — Problem card (0:00–0:25)

On screen, plain text over a simple illustration or photo-free slide:

> "A health worker files visits on paper in the field, then transcribes
> them at the clinic hours later. If she saw a danger sign in the morning,
> the clinic learns about it in the evening. The clinic laptop was never
> the problem. The distance was. ClinicLink closes that one gap:
> evening transcription becomes minute-in escalation."

Voiceover, same words, conversational — not a sales pitch.

## Shot 2 — Phone files a visit from "the field" (0:25–1:15)

- Open the demo on a phone-sized browser window, on the **Phone** tab.
  Show the pairing stepper: Request → Approve → Paired.
- Request pairing, approve with the shown code (say out loud: "the clinic
  approves — nothing files before that").
- File a visit: worker DEMO-WORKER-01, "Synthetic Household 12" (caption:
  SYNTHETIC DATA), visit type Pregnancy, note "Routine check-in".
- File a second visit: "Synthetic Household 07", tick **fever** on the
  danger-sign checklist.
- Show the red escalation banner appearing on screen:
  **"ESCALATE PER PROTOCOL"**. Say: "Not a diagnosis. A prompt to follow
  the clinic's own protocol. And it appeared the same minute — not in
  the evening transcription."
- Bonus 10 seconds, if time allows: tap **Revoke pairing** and show a
  filing attempt failing — proof the gate works both ways.

## Shot 3 — Clinic laptop dashboard updates (1:15–1:50)

- Switch to the **Clinic laptop** tab. Read the summary cards out:
  visits filed today, escalations flagged, households seen.
- Point out the red escalation banner at the top of the dashboard and
  the escalated visit in the list, with its SYNTHETIC label.
- Say: "Records live on the clinic laptop — local storage, not a central
  health cloud, no subscription. The phone is the controller; the laptop
  is the host."

## Shot 4 — Live deployed URL responding (1:50–2:20)

- Open the deployed Render URL in a fresh browser tab.
- Show `/health` responding, then one filed record on the live service.
- If the free service is asleep, say so on camera ("free tier wakes in
  about a minute") and cut to the warm response — do not fake a live
  response with a local screenshot.

## Shot 5 — Honest-limits card (2:20–2:50)

On screen, plain text:

> "Synthetic data only. No real clinic deployment yet. No diagnosis, no
> treatment advice — ever. The pilot measurement plan is documented
> (PILOT_MEASUREMENT_PLAN.md) for a clinic or NGO to adopt — it is a
> plan, with zero field data so far. What this proves: phone-to-laptop
> filing with approval pairing and minute-in protocol escalation,
> working end to end."

End card: repo URL + live demo URL (both real, both added only after
they exist).

## Scripted measurement to quote (optional, if filmed honestly)

Time one visit filed on paper + transcribed, versus one filed on the
phone, with a visible stopwatch, same synthetic household, same fields.
Quote only the two timed numbers you actually measured. Do not quote a
percentage improvement you did not measure, and do not quote any
error-rate statistic.
