# SignBridge — ML scripts

Training normally happens in the app (Teach Signs → **Train model**). These
scripts are for bulk work. Run them from the `signbridge/` folder with the
backend venv, since they reuse the backend code, so features are identical.

```bash
backend/.venv/bin/pip install -r ml/requirements.txt   # only needed for import_videos.py
```

## import_videos.py — videos → training samples

```bash
backend/.venv/bin/python ml/import_videos.py --data_dir dataset/raw
```

- Runs the MediaPipe hand + pose landmarkers, the same `.task` models as the browser, downloaded to `ml/models/` on first run, over each video.
- Stores one landmark sample per video in the database, already approved, exactly like an in-app recording.

| Layout | Command |
|---|---|
| `<word>/<signer>/*.mp4` | `--data_dir DIR` |
| `<word>/*.mp4` | `--data_dir DIR --flat --signer NAME` |
| folders aren't vocabulary words | add `--map map.csv` with columns `folder,concept,english,tamil,category` |

Use the folder name `_none` for idle / no-sign clips. Videos where no hands
are detected are skipped. Tip: trim clips to the sign itself. The live
translator watches each word for about as long as its recordings last (1.5 to
6 s), so keep all clips of a word a similar length.

## train.py — command-line training

```bash
backend/.venv/bin/python ml/train.py
```

The report:
- **Cross-validated accuracy:** held-out *signers* when there are 3+, otherwise a stratified split with a warning.
- **How often the model answers confidently**, at the backend's confidence threshold, and how often those answers are correct.
- **Per-word precision, recall and F1.**

It writes `dataset/models/model.joblib` + `model_meta.json`. Restart the
backend to load it. The in-app Train button hot-swaps the model instead.

## generate_sign_metadata.py — built-in vocabulary

```bash
python3 ml/generate_sign_metadata.py
```

Rebuilds `backend/app/data/sign_metadata.csv`. Append new words, but never
reorder existing ones, because sign IDs come from their position. Custom
words added in the app live in `dataset/custom_signs.csv` and are not
affected.
