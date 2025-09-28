from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os, torch
from PIL import Image

from models import xception, efficientnet, vit
from utils.preprocessing import transform
from utils.database import insert_history

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

WEIGHTS = {"xception": 0.4, "efficientnet": 0.3, "vit": 0.3}

app = Flask(__name__)

@app.route('/api/detect', methods=['POST'])
def detect():
    file = request.files['file']
    username = request.form.get('username', 'guest')
    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    # 이미지 전처리
    image = Image.open(path).convert('RGB')
    tensor = transform(image).unsqueeze(0)

    # 각 모델 탐지
    with torch.no_grad():
        prob_xcep = torch.sigmoid(xception(tensor)).item()
        prob_eff  = torch.sigmoid(efficientnet(tensor)).item()
        prob_vit  = torch.sigmoid(vit(tensor)).item()

    # 가중치 기반 앙상블
    final_prob = (
        WEIGHTS["xception"] * prob_xcep +
        WEIGHTS["efficientnet"] * prob_eff +
        WEIGHTS["vit"] * prob_vit
    )

    label = "Fake" if final_prob > 0.5 else "Real"
    confidence = round(final_prob, 4) if label == "Fake" else round(1 - final_prob, 4)

    # 예외 처리 보강
    warning = ""
    if confidence < 0.3:
        warning = "탐지 결과 불확실: 이미지 품질이 낮거나 노이즈가 많습니다."
    elif 0.3 <= confidence <= 0.7:
        warning = "주의: 보정된 사진(포토샵, 필터 등)일 수 있습니다."
    elif confidence > 0.9:
        warning = "변저 흔적이 없습니다."

    # DB 저장
    insert_history(username, filename, label, confidence)

    return jsonify({
        "simple_result": {
            "prediction": label,
            "confidence": confidence
        },
        "expert_result": {
            "final_prob": round(final_prob, 4),
            "model_details": {
                "xception": round(prob_xcep, 4),
                "efficientnet": round(prob_eff, 4),
                "vit": round(prob_vit, 4)
            }
        },
        "warning": warning
    })

if __name__ == "__main__":
    app.run(debug=True)
