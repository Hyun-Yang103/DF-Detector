# Deepfake Detection Service (Flask)

## Features
- PSNR/SSIM 기반 원본-수정본 비교
- Exif 기반 포토샵 등 보정 감지
- 딥러닝 모델 (Xception, FF++) 기반 추론 (optional)
- 정상 이미지만 원본 DB 저장
- 결과 저장/조회/삭제 API
- 관리자 API (전체/사용자별 삭제)

## Quickstart
```bash
pip install -r requirements.txt
mysql -u root -p < schema.sql
cp .env.example .env
python app.py
