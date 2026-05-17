"""
app.py - WhatsApp Forensics Flask API
Digital Forensics Investigation Project

Endpoints:
  GET  /                    → Health check
  POST /api/upload          → Upload key + crypt14, decrypt + analyze
  GET  /api/status          → Server status info
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from decrypt import decrypt_whatsapp_crypt14
from analyzer import analyze_database

# ── App Setup ──────────────────────────────────────────────
app = Flask(__name__)
CORS(app)  # Allow requests from frontend (different port)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'crypt14', 'crypt12', 'crypt9', 'db'}


def allowed_file(filename, allowed):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


# ── Routes ─────────────────────────────────────────────────

@app.route('/')
def home():
    return jsonify({
        "status"  : "online",
        "service" : "WhatsApp Forensics API",
        "version" : "1.0.0",
        "endpoints": {
            "POST /api/upload": "Upload key + .crypt14 files to decrypt & analyze",
            "GET  /api/status": "Get server status"
        }
    })


@app.route('/api/status')
def status():
    uploads = os.listdir(UPLOAD_FOLDER)
    return jsonify({
        "status"        : "running",
        "upload_folder" : UPLOAD_FOLDER,
        "files_stored"  : len(uploads)
    })


@app.route('/api/upload', methods=['POST'])
def upload_and_analyze():
    """
    Main forensic pipeline endpoint.
    Accepts: key_file (binary), crypt_file (.crypt14)
    Returns: JSON with decryption metadata + full message analysis
    """

    # ── 1. Validate files are present ──
    if 'key_file' not in request.files:
        return jsonify({"success": False, "error": "Missing 'key_file' in request"}), 400
    if 'crypt_file' not in request.files:
        return jsonify({"success": False, "error": "Missing 'crypt_file' in request"}), 400

    key_file   = request.files['key_file']
    crypt_file = request.files['crypt_file']

    if key_file.filename == '' or crypt_file.filename == '':
        return jsonify({"success": False, "error": "No file selected"}), 400

    # ── 2. Save uploaded files ──
    key_path   = os.path.join(UPLOAD_FOLDER, 'key')
    crypt_path = os.path.join(UPLOAD_FOLDER, 'msgstore.db.crypt14')
    db_path    = os.path.join(UPLOAD_FOLDER, 'messages_decrypted.db')

    key_file.save(key_path)
    crypt_file.save(crypt_path)

    # ── 3. Decrypt ──
    decrypt_result = decrypt_whatsapp_crypt14(key_path, crypt_path, db_path)

    if not decrypt_result["success"]:
        return jsonify({
            "success" : False,
            "stage"   : "decryption",
            "error"   : decrypt_result["error"]
        }), 500

    # ── 4. Analyze ──
    analysis = analyze_database(db_path)

    if not analysis["success"]:
        return jsonify({
            "success" : False,
            "stage"   : "analysis",
            "error"   : analysis["error"]
        }), 500

    # ── 5. Return full forensic report ──
    return jsonify({
        "success"   : True,
        "decryption": {
            "key_sha256"       : decrypt_result["key_hash"],
            "crypt_sha256"     : decrypt_result["crypt_hash"],
            "db_sha256"        : decrypt_result["db_hash"],
            "db_size_bytes"    : decrypt_result["file_size_bytes"]
        },
        "analysis"  : analysis
    })


# ── Run ────────────────────────────────────────────────────
if __name__ == '__main__':
    print("\n🔍 WhatsApp Forensics API")
    print("━" * 40)
    print(f"   Upload folder : {UPLOAD_FOLDER}")
    print(f"   API running at: http://localhost:5000")
    print("━" * 40 + "\n")
    app.run(debug=True, port=5000)
