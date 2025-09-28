import os
import pytest
from app import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_detect_low_confidence(client):
    """confidence < 0.3 → 불확실 메시지"""
    test_img = "tests/data/low_quality.jpg"
    with open(test_img, "rb") as f:
        res = client.post("/api/detect", data={"file": f})
    data = res.get_json()
    assert "불확실" in data["warning"]

def test_detect_mid_confidence(client):
    """0.3 <= confidence <= 0.7 → 보정 가능성 메시지"""
    test_img = "tests/data/photoshopped.jpg"
    with open(test_img, "rb") as f:
        res = client.post("/api/detect", data={"file": f})
    data = res.get_json()
    assert "보정된 사진" in data["warning"]

def test_detect_high_confidence(client):
    """confidence > 0.9 → 확실 메시지"""
    test_img = "tests/data/clear_fake.jpg"
    with open(test_img, "rb") as f:
        res = client.post("/api/detect", data={"file": f})
    data = res.get_json()
    assert "확실" in data["warning"]
