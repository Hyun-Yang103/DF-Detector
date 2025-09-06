import numpy as np
import cv2
from metrics import compute_psnr_ssim

def test_psnr_ssim_similar_images():
    img = np.full((64, 64, 3), 200, dtype=np.uint8)
    noisy = cv2.add(img, (np.random.rand(64, 64, 3) * 5).astype(np.uint8))
    psnr, ssim = compute_psnr_ssim(img, noisy)
    assert psnr > 25
    assert 0.7 <= ssim <= 1.0

def test_psnr_ssim_different_images():
    img1 = np.zeros((64, 64, 3), dtype=np.uint8)
    img2 = np.ones((64, 64, 3), dtype=np.uint8) * 255
    psnr, ssim = compute_psnr_ssim(img1, img2)
    assert psnr < 10
    assert ssim < 0.3
