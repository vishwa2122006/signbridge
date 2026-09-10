# SignBridge

**Sign language → Tamil and English text (and speech), live from a webcam.**

SignBridge helps Deaf people communicate with people who don't know sign
language. You teach it your signs, and it turns live signing into
Tamil + English words and sentences, with a two-way conversation mode for
talking with a hearing person (e.g. hospital staff).

- **Trainers & admins**: trainers register, record a few 1.5-second samples of each word with their webcam, and propose new words. An admin reviews every recording and word: approve or reject, with an email to the trainer. The admin then trains the model on the approved recordings, in seconds, on CPU. Translating, conversation and the vocabulary are public; recording and training need a login.
- **Translate**: sign live. Each recognized word appears in Tamil and English, and the words form a sentence you can have spoken aloud.
- **Conversation**: your signs become text; the other person replies with bilingual quick phrases, typing or dictation. Their replies are shown back to the signer as hand signs, replayed from the recordings made on Teach Signs.
- **Vocabulary**: 131 built-in words (90 healthcare + 41 everyday), plus custom words with English and Tamil text, proposed by trainers and approved by an admin.
- **Dataset import**: turn sign videos (e.g. a public Tamil/Indian Sign Language dataset) into training samples.

## How it works

```
Browser (webcam) ── MediaPipe hand + pose landmarks, on-device ──► only numbers leave the browser, never video
   │
   ├─ Teach Signs (trainer) ─► POST /samples ─► PostgreSQL, as a draft
   │                           POST /samples/submit ─► pending review (email to the admins)
   ├─ Review & Train (admin) ─► POST /review/samples ─► approved / rejected (email to the trainer)
   │                           POST /train ─► approved recordings ─► scikit-learn classifier ─► dataset/models/model.joblib (hot-loaded)
   │
   └─ Translate ──► every 250 ms, the last 1.5 s of landmarks ─► POST /predict
                     ─► confidence threshold + stability voting ─► new word
                     ─► POST /translate (offline rule templates) ─► Tamil + English sentence ─► speech
```

- **Features** (`backend/app/ml/features.py`): hand shapes relative to the wrist, hand positions relative to the shoulders, and motion over time. The features don't change with distance from the camera or position in the frame. Training adds mirrored (left-handed) and jittered copies of each recording.
- **Recognition** (`backend/app/services/recognition.py`) never forces a guess:
  - low confidence → "please repeat"
  - a single-frame spike is ignored
  - a sign held steady counts once
  - resting hands (the **Idle** class) separate repeated words
- **Sentences** (`backend/app/services/templates.py`) come from deterministic, hand-written templates, with no AI text generation. For example:
  - PAIN + STOMACH → "I have stomach pain." / "எனக்கு வயிற்றில் வலி உள்ளது."
  - WANT + WATER → "I want water." / "எனக்கு தண்ணீர் வேண்டும்."
  - FEVER + YESTERDAY → "I have had a fever since yesterday."
  - Words that don't fit a template are shown as plain words.

## Quick start

Requirements: Python 3.10+, Node 20+, PostgreSQL 14+, a webcam, Chrome or Edge.

**Database**: create an empty database for the app, and a second one for the tests:
```bash
createdb sign_bridge
createdb sign_bridge_test
```

**Backend**
```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env     # DATABASE_URL, TEST_DATABASE_URL, JWT_SECRET, SMTP_* - see the comments in the file
.venv/bin/python -m app.cli create-user --role admin --name "Your Name" --email you@example.com
.venv/bin/uvicorn app.main:app --reload --port 8000
```

Tables and the built-in vocabulary are created when the backend starts. Recordings saved as files by an older version (`dataset/landmarks/`) can be moved into the database once, as approved recordings, with `.venv/bin/python -m app.cli import-legacy`.

**Frontend** (second terminal)
```bash
cd frontend
npm install
cp .env.example .env     # points at http://localhost:8000
npm run dev
```

Open the printed URL (http://localhost:5173).

## Accounts

| Who | Can use |
|---|---|
| Public, no login | Home, Translate, Conversation, Vocabulary |
| Trainer | the public pages, plus **Teach Signs**: record words, propose new words, submit recordings for review |
| Admin | everything a trainer can (an admin's recordings and words are approved immediately), plus **Review & Train**: approve or reject recordings and proposed words, fix a word's text, see and disable trainers, train the model |

- **Registering** (Log in → Register as a trainer) asks for name, email (one account per email), phone, city, organization (optional), background, signing level, sign language, a password and consent. A code is emailed to confirm the address.
- **Logging in** works with the password, or with a one-time code sent by email (`OTP_LENGTH` digits, 6 by default). Admins are created from the command line with `python -m app.cli create-user --role admin`.
- **Emails** go out when recordings or a word are submitted (to the admins, with a copy to the trainer) and when they are approved or rejected (to the trainer, with a summary to the admins). They're sent from `SMTP_USER` with a Gmail app password in `SMTP_PASSWORD`: turn on 2-Step Verification, then create one at https://myaccount.google.com/apppasswords. While `SMTP_PASSWORD` is empty, emails and login codes are printed in the backend console instead.

## Using it

1. **Teach Signs** (trainers)
   - Log in and start the camera.
   - Pick a word, or propose a new one with English + Tamil text. You can record it straight away; others see it once an admin approves it.
   - Press **Record 10** and perform the sign each time the countdown ends. Record **Idle (no sign)** samples too: hands resting or moving naturally.
   - Recordings stay private drafts, so you can delete bad takes. Then press **Submit for review**.
2. **Review & Train** (admins)
   - Pick a word from the queue. Its recordings are grouped by trainer. ▶ replays each one as a moving hand-and-body figure; the ✋ percentage is the share of frames where hands were visible.
   - Mark recordings ✓ or ✕ one at a time, per trainer, or all at once. Add a note for rejections and press **Save review**: each trainer gets one email for the whole batch. A proposed word must be approved before its recordings can be.
   - Press **Train model**. Only approved recordings of approved words are used. You'll see cross-validated accuracy and per-word scores, plus warnings, e.g. too few signers.
3. **Translate**: start the camera and sign. Words appear as chips; the sentence updates automatically; 🔊 speaks it.
4. **Conversation**: the signer signs and presses Send; the hearing person taps a bilingual quick phrase, types, or dictates.

**Tips for accuracy**
- 15+ samples per word.
- Record 2–3 different people. With 3+ signers the accuracy number is measured on people the model hasn't seen.
- Vary your position and the lighting a little.
- Always include Idle samples.
- Words that look alike need more samples; check the per-word F1 table after training.

## Importing a video dataset

```bash
cd signbridge                               # project folder
backend/.venv/bin/pip install -r ml/requirements.txt
backend/.venv/bin/python ml/import_videos.py --data_dir dataset/raw
backend/.venv/bin/python ml/train.py        # or Train model on the Review & Train page
```

Supported layouts:
- `dataset/raw/<word>/<signer>/*.mp4` (default).
- `--flat --signer NAME` for `<word>/*.mp4`.
- `--map map.csv` (`folder,concept,english,tamil,category`) when the dataset's folder names aren't vocabulary words. Missing words are created as custom words.

It runs the same MediaPipe models as the browser, so imported and recorded samples can be mixed. Imported samples are saved as already approved. Read each dataset's license first. `DATASET_SOURCES.md` lists the Tamil and Indian Sign Language datasets that were found and what still needs checking. For example, for the Kaggle Tamil Sign Language dataset:

```bash
kaggle datasets download -d s3programmerlead/tamil-sign-language-video-dataset -p ~/Downloads/tsl --unzip
# inspect the folder structure, write a map.csv, then:
backend/.venv/bin/python ml/import_videos.py --data_dir ~/Downloads/tsl/<classes folder> --flat --signer kaggle --map map.csv
```

## Project structure

```
backend/
  app/main.py                    FastAPI app (creates tables, loads the saved model on startup)
  app/config.py, .env.example    settings (database, login tokens, codes, email)
  app/db.py, app/models/tables.py  PostgreSQL: users, otp_codes, words, samples, training_runs
  app/cli.py                     init-db, create-user, import-legacy
  app/ml/features.py             landmark → feature vector (shared by live, training, import)
  app/ml/trainer.py              training + cross-validation report
  app/ml/classifier.py           loads model.joblib
  app/services/recognition.py    threshold, stability, word emission
  app/services/templates.py      offline Tamil/English sentence templates
  app/services/vocabulary.py     words (built-in + approved custom), cached
  app/services/sample_store.py   recordings and their review status
  app/services/security.py       passwords, login tokens, email codes
  app/services/notifications.py  the emails (sent by mailer.py)
  app/routers/                   /auth /signs /samples /review /admin/users /train /predict /translate
  app/data/sign_metadata.csv     built-in vocabulary (generated by ml/generate_sign_metadata.py)
  tests/                         unit + end-to-end API tests (synthetic landmarks)
frontend/src/
  mediapipe.js                   on-device hand + pose landmark extraction
  AuthContext.jsx                the logged-in trainer or admin
  components/CameraFeed.jsx      webcam, overlay, rolling landmark window
  components/SignPlayer.jsx      replays recordings as hand signs (drawing in signClip.js)
  hooks/useSignRecognizer.js     live prediction + recognized word list
  pages/                         Home, Translate, ConversationMode, Vocabulary (public);
                                 Login, Register, Account, TeachSigns (trainers); Review (admins)
  i18n.js                        Tamil/English UI text
ml/
  import_videos.py               videos → approved training samples
  train.py                       command-line training
  generate_sign_metadata.py      rebuilds the built-in vocabulary CSV
dataset/                         git-ignored: models/, raw/ (and landmarks/ from older versions)
```

## Tests

```bash
cd backend && .venv/bin/python -m pytest tests -v
cd frontend && npm run lint && npm run build
```

The backend tests need `TEST_DATABASE_URL` in `backend/.env`: a separate database that they wipe on every run. They include a full synthetic run (a trainer proposes a word → 3 trainers record and submit → an admin approves the word and reviews the recordings → trains → live predictions → sentence), plus registration, code login and permission tests.

## Configuration

| Env var | Default | Meaning |
|---|---|---|
| `DATABASE_URL`, `JWT_SECRET`, `OTP_*`, `SMTP_*`, ... | see `backend/.env.example` | database, logins, email codes and email |
| `SIGNBRIDGE_DATA_DIR` | `signbridge/dataset` | where the trained model is stored |
| `SIGNBRIDGE_MIN_CONFIDENCE` | `0.70` | minimum classifier confidence to accept a sign |
| `SIGNBRIDGE_STABILITY_WINDOW` | `4` | predictions (~250 ms each) that must mostly agree |
| `SIGNBRIDGE_STABILITY_RATIO` | `0.75` | share of that window the word must win |
| `VITE_API_BASE` (frontend `.env`) | `http://localhost:8000` | backend URL |

To add sentence patterns, edit the dictionaries and `_FIXED` list in `backend/app/services/templates.py` and add a test in `tests/test_templates.py`. To add built-in words, append to `ml/generate_sign_metadata.py` and re-run it. Never reorder existing entries, because the IDs depend on their order.

## Limitations & privacy

- **A communication aid, not a certified interpreter, and not medical advice.** It restates what was signed and never adds a diagnosis or recommendation.
- **Recognition is only as good as the recordings.** It works best for the people it was trained on; isolated words only (no continuous grammar or fingerspelling); similar-looking signs get confused unless recorded well.
- **The Tamil text needs review.** Word translations, template grammar and staff phrases are hand-written and should be reviewed by a native Tamil speaker before real use. Signs themselves should be checked with Deaf signers.
- **No video is stored or uploaded.** Only landmark coordinates are saved, in the database, with the account that recorded them. Trainers agree to this when they register. Ask for consent before recording anyone else, and delete their recordings if they ask.
- **Respect dataset licenses** when importing videos. Don't redistribute third-party data, and credit your sources.
