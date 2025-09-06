from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
from PIL import Image
from datetime import datetime
from io import BytesIO
from dotenv import load_dotenv

from detection import deepfake_model_detect
from metrics import compute_psnr_ssim, save_diff_heatmap
from exif_utils import is_photoshop_like
from db import insert_result, fetch_results, fetch_user_original, save_user_original, delete_result, admin_delete

import json

load_dotenv()
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
HEATMAP_FOLDER = "heatmap"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(HEATMAP_FOLDER, exist_ok=True)

with open("config.json") as f:
    CONFIG = json.load(f)

@app.route("/api/detect", methods=["POST"])
def detect():
    file = request.files["file"]
    username = request.form.get("username", "guest")
    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    img = Image.open(path).convert("RGB")
    orig_img = fetch_user_original(username)

    psnr = None
    ssim = None
    confidence = None
    status = None
    source = None
    edit_type = "normal"
    heatmap_path = None

    if orig_img is not None:
        orig_np = np.array(Image.open(BytesIO(orig_img)))
        edited_np = np.array(img)

        psnr, ssim = compute_psnr_ssim(orig_np, edited_np)
        heatmap_path = os.path.join(HEATMAP_FOLDER, f"{filename}_diff.png")
        save_diff_heatmap(orig_np, edited_np, heatmap_path)

        if psnr < CONFIG["psnr_threshold"] or ssim < CONFIG["ssim_threshold"]:
            status = "Manipulated"
        else:
            status = "Normal"
        source = "psnr_ssim"

    else:
        if is_photoshop_like(img):
            status = "Normal"
            edit_type = "photoshop_edit"
        else:
            confidence = deepfake_model_detect(img)
            if confidence > CONFIG["deepfake_threshold"]:
                status = "Fake"
            else:
                status = "Normal"
                save_user_original(username, img)

        source = "deepfake_model"

    insert_result(username, filename, psnr, ssim, confidence, status, source, edit_type, heatmap_path)

    return jsonify({
        "username": username,
        "filename": filename,
        "psnr": psnr,
        "ssim": ssim,
        "confidence": confidence,
        "status": status,
        "source": source,
        "edit_type": edit_type,
        "visualization": heatmap_path
    })

@app.route("/api/results", methods=["GET"])
def get_results():
    return jsonify(fetch_results())

@app.route("/api/results/<username>", methods=["GET"])
def get_user_results(username):
    return jsonify(fetch_results(username))

@app.route("/api/delete_result", methods=["POST"])
def delete_result_api():
    rid = request.form.get("result_id")
    delete_result(rid)
    return jsonify({"message": "Deleted"})

@app.route("/api/admin/delete", methods=["POST"])
def admin_delete_api():
    admin_pw = request.form.get("admin_pw")
    if admin_pw != os.getenv("ADMIN_PW"):
        return jsonify({"error": "Unauthorized"}), 403
    target = request.form.get("target", "all")
    admin_delete(target)
    return jsonify({"message": f"Admin deleted {target}"})

@app.route("/api/heatmap/<filename>", methods=["GET"])
def get_heatmap(filename):
    path = os.path.join(HEATMAP_FOLDER, filename)
    return send_file(path, mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True)
