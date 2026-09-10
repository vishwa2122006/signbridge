# RESPONSIBLE_AI.md — SignBridge

## What this system is

An accessibility **communication assistance** prototype: it helps translate
between Tamil regional sign input and Tamil/English text (and eventually
speech), initially scoped to a healthcare vocabulary.

## What this system is NOT

- **Not a medical diagnosis system.**
- **Not a triage system.**
- **Not a treatment recommendation system.**
- **Not a medical advice system.**
- **Not a replacement for certified sign-language interpreters.**

The system translates *communication*, never *medical meaning*.

Good: "Patient appears to be communicating 'chest pain'."
Bad (never produced by this system): "Patient is having a heart attack."

Good: "Patient signed 'medicine'."
Bad (never produced by this system): "Patient should take paracetamol."

This constraint is enforced structurally, not just by convention: the
vocabulary (`sign_metadata.csv`) contains communication concepts only (body
parts, symptoms-as-reported, needs, actions) — never diagnoses, drug
dosages, or clinical recommendations — and the sentence template engine
(`templates.py`) only ever restates what was signed, never adds inference.

## Never force a prediction

This is the core safety property of the recognition engine
(`backend/app/services/recognition.py`):

- A prediction below `MIN_CONFIDENCE_THRESHOLD` (default 0.70) is rejected,
  not guessed — the system says "unclear, please repeat" instead.
- A single confident frame is not enough. The system requires
  `STABILITY_WINDOW` (default 5) consecutive predictions to agree at
  `STABILITY_RATIO` (default 80%) before accepting a sign, so momentary
  hand-tracking noise doesn't produce a false answer.
- A model output with no matching vocabulary entry surfaces as
  `UNKNOWN_SIGN`, never silently mapped to the "closest" known word.
- With no hand detected, the state is `NO_HAND`, distinct from every other
  state — silence is never mistaken for a sign.
- With no trained/validated model loaded (the state this prototype ships
  in by default), every prediction honestly returns `NO_MODEL` rather than
  fabricating a result. This is intentional — see DATASET_SOURCES.md for
  why no model is bundled.

All of this is unit-tested in `backend/tests/test_recognition.py`,
including the exact worked examples from the design spec (a stable run of
identical predictions is accepted; a flickering sequence of different
predictions is rejected).

## No invented signs

Every entry in `sign_metadata.csv` ships with `validation_status` and
`sign_language` fields. As delivered, **every single concept is
`unverified`** with `sign_language = "not yet mapped - pending
validation"** — this project does not claim, anywhere, that a specific
hand gesture has been confirmed as the correct Tamil Nadu regional sign for
any concept. See DATASET_SOURCES.md for the full audit of what data exists
and what still needs human validation before a concept can move to
`research-reference` or `validated`.

The Tamil words shown in the vocabulary are **language translations for
display/speech only** — what to show or speak once a sign is recognized —
never a claim about what the sign itself looks like.

## Community validation over model confidence

The feedback mechanism (`/feedback`, and the Community Validation panel in
Dataset/Research Mode) exists because a human — ideally a Deaf signer,
interpreter, or special-education teacher — confirming or rejecting a
prediction is treated as more authoritative than the model's own confidence
score. Promoting a concept from `unverified` to `validated` in
`sign_metadata.csv` should only happen after this kind of review, not
automatically from training accuracy.

## Privacy by design

Default flow: camera → local (in-browser) MediaPipe processing → landmark
coordinates extracted → sent to the backend for classification → frame
discarded. Raw video is **never saved or uploaded** in normal use.

The one exception is the clearly labeled **Dataset Collection Mode**, which
requires an explicit on-screen consent checkbox before recording is even
enabled, records to the contributor's own device (not silently uploaded),
and logs only metadata (signer ID, sign, consent flag) to the backend —
never the video itself.

## Overclaiming guardrails

The UI and this documentation explicitly state, in multiple places:
"Prototype." "Limited, unverified vocabulary." "Not a replacement for
certified sign-language interpreters." "Not a medical diagnostic system."
"Recognition depends on supported signs and validated data." "Unknown
signs are intentionally rejected rather than guessed."

Rejecting instead of guessing is presented as a feature, not a limitation
to apologize for — in a healthcare accessibility context, a wrong silent
guess is worse than an honest "I don't know."

## Known limitations of this prototype

- No model ships trained on validated Tamil Sign Language data (see
  DATASET_SOURCES.md — nothing there was confirmed as Category A yet).
- The healthcare ontology (90 candidate concepts) is a starting point for
  human review, not a finished, validated vocabulary.
- Sentence templates cover only a few concept combinations
  (`templates.py`) — most recognized-concept combinations will show
  individual concept badges rather than a formed sentence, by design
  (no LLM-based sentence generation is used).
- Tamil grammatical forms used in templates (e.g. locative case endings)
  are a best-effort draft and have not been reviewed by a native-speaker
  or Deaf-community validator as part of this prototype.
