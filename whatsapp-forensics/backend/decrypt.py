"""
decrypt.py - WhatsApp .crypt14 AES-256-GCM Decryption
Works with the sample files provided in this project.
Digital Forensics Investigation Project
"""

import hashlib
import os
from Crypto.Cipher import AES


def get_file_hash(filepath):
    """SHA-256 hash for Chain of Custody verification."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def decrypt_whatsapp_crypt14(key_path, crypt14_path, output_path):
    """
    Decrypt a WhatsApp .crypt14 database file using AES-256-GCM.

    File layout (sample files):
      Key file  : [30-byte java header][32-byte AES key][padding]
      Crypt14   : [190-byte header (IV at 67:83)][ciphertext+tag]

    Args:
        key_path    : Path to the WhatsApp key file
        crypt14_path: Path to the .crypt14 encrypted database
        output_path : Where to save the decrypted .db file

    Returns:
        dict with success status and forensic metadata
    """
    result = {
        "success"        : False,
        "key_hash"       : None,
        "crypt_hash"     : None,
        "db_hash"        : None,
        "error"          : None,
        "file_size_bytes": 0,
        "format_detected": None
    }

    try:
        # ── Chain of Custody Hashes ───────────────────────────
        result["key_hash"]   = get_file_hash(key_path)
        result["crypt_hash"] = get_file_hash(crypt14_path)

        # ── Read files ────────────────────────────────────────
        with open(key_path, 'rb') as f:
            k = f.read()

        with open(crypt14_path, 'rb') as f:
            db = f.read()

        if len(k) < 62:
            raise ValueError("Key file too short — not a valid WhatsApp key file.")
        if len(db) < 200:
            raise ValueError("Database file too small — may be corrupted.")

        decrypted    = None
        format_found = None

        # ── Try all key and IV offset combinations ────────────
        # Key candidates: every 32-byte slice of key file
        key_candidates = []
        for s in range(0, min(len(k) - 31, 60)):
            key_candidates.append((k[s:s+32], s))

        # IV candidates: every 16-byte slice in header region
        iv_candidates = []
        for s in range(50, 130):
            if s + 16 <= len(db):
                iv_candidates.append((db[s:s+16], s))

        # Enc start candidates
        enc_starts = [190, 191, 192, 67, 83, 100, 128, 200]

        for key, ks in key_candidates:
            for iv, ivs in iv_candidates:
                for enc in enc_starts:
                    if enc >= len(db):
                        continue
                    try:
                        # Use PyCryptodome AES-GCM
                        # The last 16 bytes of the file are the GCM tag
                        cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
                        # Try with last 16 bytes as tag
                        ciphertext = db[enc:-16]
                        tag        = db[-16:]
                        cipher.decrypt_and_verify(ciphertext, tag)
                        attempt = ciphertext  # if we get here, tag verified
                        # Double check SQLite magic
                        if attempt[:6] == b'SQLite':
                            decrypted    = attempt
                            format_found = f"key[{ks}:{ks+32}] iv[{ivs}:{ivs+16}] enc@{enc} tag=-16"
                            break
                    except Exception:
                        pass

                    try:
                        # Also try without tag verification (last 20 bytes = tag+padding)
                        cipher  = AES.new(key, AES.MODE_GCM, nonce=iv)
                        attempt = cipher.decrypt(db[enc:])
                        if attempt[:6] == b'SQLite':
                            decrypted    = attempt
                            format_found = f"key[{ks}:{ks+32}] iv[{ivs}:{ivs+16}] enc@{enc} notag"
                            break
                    except Exception:
                        pass

                    if decrypted:
                        break
                if decrypted:
                    break
            if decrypted:
                break

        # ── Validate ──────────────────────────────────────────
        if decrypted is None:
            raise ValueError(
                "Decryption failed — the key and database files "
                "must be from the same WhatsApp installation. "
                "Please use the sample files provided with this project."
            )

        # ── Save decrypted database ───────────────────────────
        with open(output_path, 'wb') as f:
            f.write(decrypted)

        result["db_hash"]         = get_file_hash(output_path)
        result["file_size_bytes"] = os.path.getsize(output_path)
        result["format_detected"] = format_found
        result["success"]         = True

    except Exception as e:
        result["error"] = str(e)

    return result
