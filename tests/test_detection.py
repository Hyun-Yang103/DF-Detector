from PIL import Image
import numpy as np
from detection import deepfake_model_detect

def test_model_runs():
    img = Image.fromarray(np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8))
    prob = deepfake_model_detect(img)
    assert 0.0 <= prob <= 1.0
