# SignBridge

**"Breaking the communication barrier between Deaf patients and healthcare workers."**

A hackathon prototype for the problem statement *"Tamil Sign Language (not
ISL) to Text Translator"* — scoped to a healthcare communication use case,
built with safety and honesty as first-class requirements, not afterthoughts.

> **Prototype. Limited, unverified vocabulary. Not a replacement for
> certified sign-language interpreters. Not a medical diagnosis system.**
> See `RESPONSIBLE_AI.md`.

## What's real vs. what's simulated — read this first

This matters more than anything else in this README. Being honest about it
is the whole point of the project.

**Real and working, verified end-to-end in this build:**
- The full-stack architecture: FastAPI backend + React/Vite frontend, wired
  together and tested live (Playwright smoke test, screenshots below).
- Client-side hand-landmark extraction via MediaPipe running in the
  browser (privacy-by-design — video never leaves the device).
- The safety-critical recognition engine: confidence thresholding,
  temporal stability (rejects flickering predictions, accepts stable
  ones), `UNKNOWN_SIGN` / `NO_HAND` / `NO_MODEL` state handling — all
  unit-tested (`backend/tests/`, 13/13 passing).
- The ML training pipeline (`ml/`): landmark extraction, signer-based
  train/val/test split, precision/recall/F1/confusion-matrix reporting,
  confidence-threshold rejection analysis — verified end-to-end against a
  synthetic fixture (see `ml/tests/`), because no real validated Tamil
  Sign Language video data was available to train on in this environment.
- The bilingual healthcare ontology (90 candidate concepts,
  `sign_metadata.csv`), the deterministic sentence-template engine, the
  Conversation Mode two-way flow, the Dataset Collection Mode with
  mandatory consent, and the Community Validation feedback loop.

**Not yet real — and deliberately not faked:**
- **No trained model recognizing actual Tamil Sign Language signs ships
  with this prototype.** `backend/app/services/recognition.py` has no
  model loaded by default, so every real `/predict` call honestly returns
  `NO_MODEL`. This is because no dataset available during research was
  confirmed (license checked, signer count verified, Deaf-community
  reviewed) as trustworthy ground truth — seeDATASET_SOURCES.md. Training
  one is real, scoped work for your team during the hackathon, using
  `ml/train_classifier.py` once you've collected/validated real clips.
- **No sign in `sign_metadata.csv` is marked `validated`.** Every concept
  is `unverified` by design, pending real sourcing and community review.
- Use **Simulation Mode** (a toggle on the Live Translator page) to demo
  the entire downstream experience — confidence display, bilingual output,
  emergency banner, speech — using manually selected concepts instead of
  a live camera. It's clearly labeled `SIMULATED` everywhere it appears so
  it can never be mistaken for real recognition.

## Quick start

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python3 -m uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env   # points at http://localhost:8000 by default
npm run dev
```
Open the printed local URL, click **Start Live Translator**, and toggle
**Simulation Mode** to see the full flow without a trained model.

**Run the tests:**
```bash
cd backend && python3 -m pytest tests/ -v         # 13 tests, safety logic
cd frontend && node smoke_test.mjs                 # live browser smoke test (needs both servers running)
```

**Train on real data once you have it** (see `ml/README.md` and
`DATASET_SOURCES.md` first):
```bash
cd ml
python3 extract_landmarks.py --data_dir dataset/raw --out landmarks.npz
python3 train_classifier.py --data landmarks.npz --out sign_model.keras
# then wire it into backend/app/main.py per ml/README.md step 4
```

## Project structure

```
signbridge/
  DATASET_SOURCES.md      dataset audit (Category A/B/C, per-source fields)
  DATA_LICENSE.md         data/consent policy for external + collected data
  RESPONSIBLE_AI.md       what this is/isn't, safety design, limitations
  backend/                FastAPI app (recognition engine, vocabulary, templates, feedback)
    app/data/             sign_metadata.csv, samples.csv, dataset_sources.csv
    tests/                unit tests for the safety-critical logic
  ml/                     landmark extraction + training pipeline
    tests/                synthetic-fixture pipeline test (not real sign data)
  frontend/                React + Vite app
    src/pages/             Home, Live Translator, Conversation Mode,
                            Healthcare Vocabulary, Dataset/Research Mode,
                            About/Responsible AI
  dataset/raw/             empty on purpose — see its README before adding videos
```

## The main demo (healthcare scenario)

1. Home page → "Start Live Translator."
2. Toggle Simulation Mode (until a real model is trained and loaded).
3. Click **HELP** → emergency banner fires, bilingual text + speech.
4. Switch to Conversation Mode → select **PAIN** + **STOMACH** → deterministic
   template forms "I have stomach pain." / "எனக்கு வயிற்றில் வலி உள்ளது."
5. Staff panel: type or speak "How long have you had the pain?" → logged
   to the conversation transcript for the patient to see.
6. About page: show the judges the Responsible AI page directly — the
   explicit non-diagnosis disclaimer and limitations are part of the
   pitch, not fine print.

## Priority next steps for your team during the hackathon

1. Download the Tamil Sign Language Video Dataset (Kaggle) — the lowest
   access-friction Category B source in `DATASET_SOURCES.md` — and
   actually read its license before using it.
2. If at all possible, get even one Tamil Nadu Deaf-community member,
   interpreter, or special-education teacher to review a sample of signs
   and confirm or correct them — this is worth more to your pitch than
   any accuracy number.
3. Record a small supplementary set yourselves via Dataset Collection Mode
   for the 13 `priority_demo_candidate` concepts (help, emergency, doctor,
   pain, water, etc. — see `/signs/demo-priority`), with at least 3
   distinct signers so `train_classifier.py` can report a real, honest
   test accuracy instead of the "too few signers" warning.
4. Train, evaluate, and report the **confidence-threshold rejection
   number** from `train_classifier.py` (not just raw accuracy) — that's
   the defensible metric for your pitch.
5. Wire the trained model into `backend/app/services/recognition.py`
   (see `ml/README.md` step 4) and watch `NO_MODEL` become real
   recognition.
