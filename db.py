import mysql.connector
import os
from io import BytesIO

def get_conn():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST","localhost"),
        user=os.getenv("DB_USER","root"),
        password=os.getenv("DB_PASS",""),
        database=os.getenv("DB_NAME","deepfake_db")
    )

def insert_result(user, filename, psnr, ssim, conf, status, source, edit_type, vis):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("""
        INSERT INTO detection_results (user_id, filename, psnr, ssim, confidence, status, source, edit_type, visualization)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (user, filename, psnr, ssim, conf, status, source, edit_type, vis))
    conn.commit(); conn.close()

def fetch_results(user=None):
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    if user:
        cur.execute("SELECT * FROM detection_results WHERE user_id=%s ORDER BY created_at DESC",(user,))
    else:
        cur.execute("SELECT * FROM detection_results ORDER BY created_at DESC")
    rows = cur.fetchall(); conn.close()
    return rows

def fetch_user_original(user):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT original_image FROM user_images WHERE user_id=%s ORDER BY uploaded_at DESC LIMIT 1",(user,))
    row = cur.fetchone(); conn.close()
    return row[0] if row else None

def save_user_original(user, img):
    buf = BytesIO(); img.save(buf, format="PNG")
    data = buf.getvalue()
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO user_images (user_id, original_image) VALUES (%s,%s)",(user,data))
    conn.commit(); conn.close()

def delete_result(rid):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM detection_results WHERE id=%s",(rid,))
    conn.commit(); conn.close()

def admin_delete(target):
    conn = get_conn(); cur = conn.cursor()
    if target=="all":
        cur.execute("DELETE FROM detection_results")
    else:
        cur.execute("DELETE FROM detection_results WHERE user_id=%s",(target,))
    conn.commit(); conn.close()
