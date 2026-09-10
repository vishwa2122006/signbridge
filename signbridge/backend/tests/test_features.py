import numpy as np

from app.ml import features
from tests.synthetic import make_clip


def _transform(frames, dx, dy, scale, cx=0.5, cy=0.5):
    def move(points):
        if points is None:
            return None
        return [[cx + (x - cx) * scale + dx, cy + (y - cy) * scale + dy, z * scale] for x, y, z in points]
    return [{**f, "left": move(f["left"]), "right": move(f["right"]), "pose": move(f["pose"])} for f in frames]


def test_same_sign_further_from_camera_and_off_centre_gives_same_features():
    frames = make_clip("pain", 0, np.random.default_rng(1))
    moved = _transform(frames, dx=0.08, dy=-0.05, scale=0.8)
    np.testing.assert_allclose(features.clip_vector(frames), features.clip_vector(moved), rtol=1e-3, atol=1e-3)


def test_vector_size_is_fixed_regardless_of_frame_rate_and_length():
    rng = np.random.default_rng(2)
    for n_frames, fps in [(10, 15.0), (45, 30.0), (90, 60.0)]:
        assert features.clip_vector(make_clip("water", 0, rng, n_frames, fps)).shape == (features.VECTOR_SIZE,)
    empty = features.clip_vector([])
    assert empty.shape == (features.VECTOR_SIZE,) and not empty.any()


def test_mirror_swaps_hands_and_is_its_own_inverse():
    frames = make_clip("water", 0, np.random.default_rng(3))
    mirrored = features.mirror(frames)
    assert all(f["right"] is None and f["left"] is not None for f in mirrored)
    np.testing.assert_allclose(features.clip_vector(features.mirror(mirrored)), features.clip_vector(frames), atol=1e-5)


def test_brief_hand_dropout_is_filled():
    frames = make_clip("water", 0, np.random.default_rng(4))
    for i in (20, 21):
        frames[i]["right"] = None
    matrix = features.frame_matrix(frames)
    assert matrix[:, features.PER_HAND].all()  # right-hand presence flag set on every step


def test_jitter_keeps_frame_format():
    frames = make_clip("hello", 0, np.random.default_rng(5))
    jittered = features.jitter(frames, np.random.default_rng(6))
    assert 5 <= len(jittered) <= len(frames)
    assert all(len(f["right"]) == 21 and f["left"] is None for f in jittered)
