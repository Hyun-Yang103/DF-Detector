from PIL import Image
import io
from exif_utils import is_photoshop_like

def test_exif_none_returns_false():
    img = Image.new("RGB", (16, 16), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    img2 = Image.open(buf)
    assert is_photoshop_like(img2) is False
