# SignBridge

**Sign language → Tamil and English text (and speech), live from a webcam.**

SignBridge helps Deaf people communicate with people who don't know sign
language. You teach it your signs, and it turns live signing into
Tamil + English words and sentences, with a two-way conversation mode for
talking with a hearing person (e.g. hospital staff).

- **Teach Signs**: record a few 1.5-second samples of each word with your webcam and train a model in seconds, on CPU.
- **Translate**: sign live. Each recognized word appears in Tamil and English, and the words form a sentence you can have spoken aloud.
- **Conversation**: your signs become text; the other person replies with bilingual quick phrases, typing or dictation.
- **Vocabulary**: 131 built-in words (90 healthcare + 41 everyday), plus any custom words you add with your own English and Tamil text.
- **Dataset import**: turn sign videos (e.g. a public Tamil/Indian Sign Language dataset) into training samples.

## How it works

```
Browser (webcam) ── MediaPipe hand + pose landmarks, on-device ──► only numbers leave the browser, never video
   │
   ├─ Teach Signs ─► POST /samples ─► dataset/landmarks/<word>/*.json
   │                 POST /train   ─► scikit-learn classifier ─► dataset/models/model.joblib (hot-loaded)
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

Requirements: Python 3.10+, Node 20+, a webcam, Chrome or Edge.

**Backend**
```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000
```

**Frontend** (second terminal)
```bash
cd frontend
npm install
cp .env.example .env     # points at http://localhost:8000
npm run dev
```

Open the printed URL (http://localhost:5173).

## Using it

1. **Teach Signs**
   - Enter your name and start the camera.
   - Pick a word (or add your own with English + Tamil text).
   - Press **Record 10** and perform the sign each time the countdown ends.
   - Do this for each word you want, and record **Idle (no sign)** samples too: hands resting or moving naturally.
2. Click **Train model**. You'll see cross-validated accuracy and per-word scores, plus warnings, e.g. too few signers.
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
backend/.venv/bin/python ml/train.py        # or click Train model in the app
```

Supported layouts:
- `dataset/raw/<word>/<signer>/*.mp4` (default).
- `--flat --signer NAME` for `<word>/*.mp4`.
- `--map map.csv` (`folder,concept,english,tamil,category`) when the dataset's folder names aren't vocabulary words. Missing words are created as custom words.

It runs the same MediaPipe models as the browser, so imported and recorded samples can be mixed. Read each dataset's license first. `DATASET_SOURCES.md` lists the Tamil and Indian Sign Language datasets that were found and what still needs checking. For example, for the Kaggle Tamil Sign Language dataset:

```bash
kaggle datasets download -d s3programmerlead/tamil-sign-language-video-dataset -p ~/Downloads/tsl --unzip
# inspect the folder structure, write a map.csv, then:
backend/.venv/bin/python ml/import_videos.py --data_dir ~/Downloads/tsl/<classes folder> --flat --signer kaggle --map map.csv
```

## Project structure

```
backend/
  app/main.py                  FastAPI app (loads the saved model on startup)
  app/ml/features.py           landmark → feature vector (shared by live, training, import)
  app/ml/trainer.py            training + cross-validation report
  app/ml/classifier.py         loads model.joblib
  app/services/recognition.py  threshold, stability, word emission
  app/services/templates.py    offline Tamil/English sentence templates
  app/services/vocabulary.py   built-in + custom words
  app/services/sample_store.py recorded samples on disk
  app/routers/                 /predict /signs /samples /train /translate
  app/data/sign_metadata.csv   built-in vocabulary (generated by ml/generate_sign_metadata.py)
  tests/                       unit + end-to-end API tests (synthetic landmarks)
frontend/src/
  mediapipe.js                 on-device hand + pose landmark extraction
  components/CameraFeed.jsx    webcam, overlay, rolling landmark window
  hooks/useSignRecognizer.js   live prediction + recognized word list
  pages/                       Home, Translate, TeachSigns, ConversationMode, Vocabulary
  i18n.js                      Tamil/English UI text
ml/
  import_videos.py             videos → training samples
  train.py                     command-line training
  generate_sign_metadata.py    rebuilds the built-in vocabulary CSV
dataset/                       your data (git-ignored): landmarks/, models/, custom_signs.csv, raw/
```

## Tests

```bash
cd backend && .venv/bin/python -m pytest tests -v
cd frontend && npm run lint && npm run build
```

The backend tests include a full synthetic run: add a custom word → record samples for 3 signers → train → live predictions → sentence.

## Configuration

| Env var | Default | Meaning |
|---|---|---|
| `SIGNBRIDGE_DATA_DIR` | `signbridge/dataset` | where samples, models and custom words are stored |
| `SIGNBRIDGE_MIN_CONFIDENCE` | `0.70` | minimum classifier confidence to accept a sign |
| `SIGNBRIDGE_STABILITY_WINDOW` | `4` | predictions (~250 ms each) that must mostly agree |
| `SIGNBRIDGE_STABILITY_RATIO` | `0.75` | share of that window the word must win |
| `VITE_API_BASE` (frontend `.env`) | `http://localhost:8000` | backend URL |

To add sentence patterns, edit the dictionaries and `_FIXED` list in `backend/app/services/templates.py` and add a test in `tests/test_templates.py`. To add built-in words, append to `ml/generate_sign_metadata.py` and re-run it. Never reorder existing entries, because the IDs depend on their order.

## Limitations & privacy

- **A communication aid, not a certified interpreter, and not medical advice.** It restates what was signed and never adds a diagnosis or recommendation.
- **Recognition is only as good as the recordings.** It works best for the people it was trained on; isolated words only (no continuous grammar or fingerspelling); similar-looking signs get confused unless recorded well.
- **The Tamil text needs review.** Word translations, template grammar and staff phrases are hand-written and should be reviewed by a native Tamil speaker before real use. Signs themselves should be checked with Deaf signers.
- **No video is stored or uploaded.** Only landmark coordinates are saved (under `dataset/landmarks/`, one file per recording, named by signer). Ask for consent before recording anyone else, and delete their files if they ask.
- **Respect dataset licenses** when importing videos. Don't redistribute third-party data, and credit your sources.
