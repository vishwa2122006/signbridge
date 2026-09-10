# SignBridge — Training Pipeline

## 0. Setup
```bash
pip install mediapipe opencv-python tensorflow scikit-learn numpy
```

## 1. Populate real data (see ../DATASET_SOURCES.md first)
```
dataset/raw/
    help/
        signer_001/
            clip1.mp4
        signer_002/
            clip1.mp4
    pain/
        signer_001/
            clip1.mp4
        ...
```
Only add a concept folder once its source is logged in `DATASET_SOURCES.md`
(Category A or B) or collected via the app's Dataset Collection Mode with
recorded consent. Aim for **at least 3 distinct signers per concept** —
fewer than that and `train_classifier.py` will refuse to report a
meaningful test accuracy (see step 3), which is intentional.

## 2. Extract landmarks
```bash
python extract_landmarks.py --data_dir dataset/raw --out landmarks.npz --seq_len 30
```

## 3. Train — signer-based split, not random split
```bash
python train_classifier.py --data landmarks.npz --out sign_model.keras --confidence_threshold 0.70
```
This holds out entire signers for validation/test (never splits one
person's clips across train and test — that would leak and inflate
accuracy). It prints per-class precision/recall/F1, a confusion matrix,
and — importantly — a **confidence-threshold rejection report**: at the
same threshold the live backend uses (`SIGNBRIDGE_MIN_CONFIDENCE`, default
0.70), how many test signs would actually be accepted vs. rejected as
"unclear," and how accurate the accepted ones are. That's the number to
quote in your pitch, not raw accuracy.

`--confidence_threshold` should always match the backend's
`SIGNBRIDGE_MIN_CONFIDENCE` env var so your reported numbers reflect what
the live system will actually do.

## 4. Wire the trained model into the backend
`backend/app/services/recognition.py` ships with **no model loaded on
purpose** — every `/predict` call honestly returns `NO_MODEL` until you
load one. To load your trained model at backend startup, add something
like this to `backend/app/main.py`:

```python
import tensorflow as tf, json
from app.services.recognition import engine

model = tf.keras.models.load_model("../../ml/sign_model.keras")
with open("../../ml/labels.json", encoding="utf-8") as f:
    labels = json.load(f)

class KerasAdapter:
    def predict(self, window_features):
        import numpy as np
        x = np.expand_dims(np.array(window_features, dtype="float32"), axis=0)
        return model.predict(x, verbose=0)[0]

engine.load_model(KerasAdapter(), labels)
```

## Testing the pipeline without real data
`tests/generate_synthetic_landmarks.py` generates a fake, clearly-labeled
synthetic fixture purely to verify the training code runs correctly
end-to-end (signer split, metrics, model export). **It is not real sign
data and must never be presented as such** — it exists only so bugs in
the pipeline are caught before you point it at real footage. Run it with:
```bash
python tests/generate_synthetic_landmarks.py
python train_classifier.py --data ml/tests/synthetic_landmarks.npz --out /tmp/test_model.keras --epochs 15
```

## Static vs. dynamic signs
If a concept turns out to be a genuinely static pose, the LSTM here still
works (it just learns "no change over time" as the pattern) but you can
also try a simpler/faster classifier (random forest on the averaged
landmark vector) as a fallback if LSTM training is unstable on very few
samples. Try the LSTM first — it handles both static and dynamic signs
correctly without you needing to decide in advance.
