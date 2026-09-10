"""Paths and tunables.

Everything user-generated (recorded landmark samples, the trained model,
custom words) lives under DATA_DIR, outside the app package. Paths are
functions rather than constants so tests can point SIGNBRIDGE_DATA_DIR at a
temporary directory.
"""

import os

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def data_dir() -> str:
    return os.environ.get("SIGNBRIDGE_DATA_DIR", os.path.join(_PROJECT_ROOT, "dataset"))


def samples_dir() -> str:
    return os.path.join(data_dir(), "landmarks")


def model_dir() -> str:
    return os.path.join(data_dir(), "models")


def custom_signs_path() -> str:
    return os.path.join(data_dir(), "custom_signs.csv")


# Label of the "resting hands / not signing" class recorded on the Teach page.
NONE_LABEL = "_none"

# Recognition: a word is only accepted when the classifier is at least this
# confident AND the same word wins STABILITY_RATIO of the last
# STABILITY_WINDOW predictions (one prediction every ~250 ms).
MIN_CONFIDENCE = float(os.environ.get("SIGNBRIDGE_MIN_CONFIDENCE", "0.70"))
STABILITY_WINDOW = int(os.environ.get("SIGNBRIDGE_STABILITY_WINDOW", "4"))
STABILITY_RATIO = float(os.environ.get("SIGNBRIDGE_STABILITY_RATIO", "0.75"))
