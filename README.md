# 🔐 Digital Forensics Investigation of WhatsApp on Android Devices

> A complete forensic investigation tool that decrypts WhatsApp `.crypt14` databases using **AES-256-GCM** cryptography, analyzes recovered messages, and presents digital evidence through an interactive web dashboard.

---

## 📌 Table of Contents

1. [Project Overview](#project-overview)
2. [Project Architecture](#project-architecture)
3. [Complete Work Flow](#complete-work-flow)
4. [Technologies Used](#technologies-used)
5. [Folder Structure](#folder-structure)
6. [Installation & Setup](#installation--setup)
7. [Step-by-Step Implementation](#step-by-step-implementation)
8. [How to Run the Project](#how-to-run-the-project)
9. [How Each File Works](#how-each-file-works)
10. [API Endpoints](#api-endpoints)
11. [Cryptography Explained](#cryptography-explained)
12. [Sample Data](#sample-data)
13. [Dashboard Features](#dashboard-features)
14. [Troubleshooting](#troubleshooting)
15. [Legal Disclaimer](#legal-disclaimer)

---

## 📖 Project Overview

WhatsApp stores all your messages as an **encrypted backup** file on your Android device:

```
Internal Storage → WhatsApp → Databases → msgstore.db.crypt14
```

The `.crypt14` file is locked using **AES-256-GCM encryption** — the same standard used by banks and governments. Without the secret key file, this database is completely unreadable.

### What This Project Does:

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│   msgstore.db.crypt14  +  key  →  Decrypt  →  📊   │
│   (Encrypted Database)    (Secret Key)    Dashboard │
│                                                     │
└─────────────────────────────────────────────────────┘

<img width="1286" height="552" alt="image" src="https://github.com/user-attachments/assets/d93cb80f-92c5-4bae-9f9c-702e4464764e" />
```

1. Takes the encrypted WhatsApp database and key file as input
2. Decrypts the database using AES-256-GCM algorithm
3. Reads all messages, contacts, and timestamps from the SQLite database
4. Generates SHA-256 hashes for Chain of Custody
5. Displays everything on a beautiful web dashboard with charts
6. Allows export as JSON forensic report or CSV

---

## 🏗️ Project Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                           │
│          HTML + CSS + JavaScript (Browser)                      │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│   │  index.html  │  │dashboard.html│  │  crypto.html │        │
│   │  Upload Page │  │Evidence View │  │  Crypto Info │        │
│   └──────┬───────┘  └──────┬───────┘  └──────────────┘        │
│          │                  │                                   │
└──────────┼──────────────────┼───────────────────────────────────┘
           │  HTTP POST        │  JSON Response
           ▼                  ▲
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND LAYER                            │
│                   Python Flask API Server                       │
│   ┌──────────────────────────────────────────────────────────┐ │
│   │                      app.py                              │ │
│   │              POST /api/upload                            │ │
│   └──────────────┬───────────────────┬───────────────────────┘ │
│                  │                   │                          │
│   ┌──────────────▼──────┐  ┌────────▼──────────────────────┐  │
│   │     decrypt.py      │  │        analyzer.py            │  │
│   │   AES-256-GCM       │  │     SQLite DB Reader          │  │
│   │   Decryption Logic  │  │   Messages + Contacts         │  │
│   └──────────────┬──────┘  └────────┬──────────────────────┘  │
│                  │                   │                          │
└──────────────────┼───────────────────┼──────────────────────────┘
                   │                   │
┌──────────────────▼───────────────────▼──────────────────────────┐
│                        CORE TOOLS LAYER                         │
│   pycryptodome (AES)  │  sqlite3  │  hashlib  │  os/pathlib   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Work Flow

```
STEP 1: USER OPENS UPLOAD PAGE
        │
        ▼
STEP 2: SELECT KEY FILE
        (The 256-bit AES encryption key)
        │
        ▼
STEP 3: SELECT .CRYPT14 FILE
        (Encrypted WhatsApp database)
        │
        ▼
STEP 4: CLICK "DECRYPT & ANALYZE"
        │
        ▼
STEP 5: FRONTEND SENDS HTTP POST REQUEST
        POST /api/upload → Flask API (localhost:5000)
        │
        ▼
STEP 6: FLASK RECEIVES FILES
        Saves to backend/uploads/ folder
        │
        ▼
STEP 7: SHA-256 HASHING (Chain of Custody)
        Hash key file   → "a3f1c2d4..."
        Hash crypt14    → "b4c5d6e7..."
        (Proves files were not modified)
        │
        ▼
STEP 8: DECRYPTION (decrypt.py)
        ├── Read AES key from key_file[30:62]  (32 bytes)
        ├── Read IV from crypt14[67:83]         (16 bytes)
        ├── Read ciphertext from crypt14[190:]
        ├── Run AES.new(key, MODE_GCM, nonce=iv)
        ├── cipher.decrypt(ciphertext)
        └── Verify: decrypted[:6] == b'SQLite' ✅
        │
        ▼
STEP 9: ANALYSIS (analyzer.py)
        ├── sqlite3.connect(decrypted_db)
        ├── Read messages table
        │   └── contact JID, message text, timestamp, direction
        ├── Count total messages, sent, received
        ├── Find top 5 contacts
        ├── Build daily timeline
        └── List all database tables found
        │
        ▼
STEP 10: SHA-256 HASH OF DECRYPTED FILE
         Hash decrypted_db → "c5d6e7f8..."
         (Proves decryption output is authentic)
        │
        ▼
STEP 11: JSON RESPONSE TO FRONTEND
         {
           "success": true,
           "decryption": { hashes... },
           "analysis": { messages, contacts, charts... }
         }
        │
        ▼
STEP 12: DASHBOARD DISPLAYS EVIDENCE
         ├── 4 Stat cards (totals)
         ├── SHA-256 Chain of Custody hashes
         ├── Bar chart (top contacts)
         ├── Doughnut chart (sent vs received)
         ├── Line chart (daily timeline)
         ├── Searchable message table
         └── Export buttons (JSON / CSV)
```

---

## 🛠️ Technologies Used

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.10+ | Core backend language |
| **Flask** | 3.0.3 | REST API web server |
| **pycryptodome** | 3.20.0 | AES-256-GCM decryption |
| **sqlite3** | Built-in | Read decrypted WhatsApp DB |
| **hashlib** | Built-in | SHA-256 Chain of Custody hashes |
| **flask-cors** | 4.0.1 | Allow frontend-backend communication |
| **HTML/CSS** | 5/3 | Frontend user interface |
| **JavaScript** | ES6+ | Frontend logic and API calls |
| **Chart.js** | 4.4.1 | Visual charts and graphs |

---

## 📁 Folder Structure

```
whatsapp-forensics/
│
├── backend/                          ← Python server (runs here)
│   ├── app.py                        ← Main Flask API server
│   ├── decrypt.py                    ← AES-256-GCM decryption module
│   ├── analyzer.py                   ← SQLite database analyzer
│   ├── requirements.txt              ← Python dependencies list
│   └── uploads/                      ← Uploaded files stored here
│       ├── key                       ← Uploaded key file
│       ├── msgstore.db.crypt14       ← Uploaded encrypted database
│       └── messages_decrypted.db     ← Decrypted database (generated)
│
└── frontend/                         ← Browser files (open from here)
    ├── index.html                    ← Upload page (start here)
    ├── dashboard.html                ← Evidence dashboard
    ├── crypto.html                   ← Cryptography explanation page
    └── style.css                     ← Shared styling for all pages
```

---

## ⚙️ Installation & Setup

### Prerequisites

Make sure you have the following installed:

| Tool | Version | Download |
|------|---------|---------|
| **Python** | 3.10 or higher | python.org |
| **pip** | Latest | Comes with Python |
| **Web Browser** | Any modern | Chrome/Firefox/Edge |

### Verify Python Installation

Open Command Prompt and run:

```bash
python --version
# Should show: Python 3.10.x or higher

pip --version
# Should show: pip 23.x or higher
```

---

## 📋 Step-by-Step Implementation

### PHASE 1 — Project Setup

#### Step 1 — Create Project Folders

Create the following folder structure on your desktop or any location:

```
whatsapp-forensics/
├── backend/
│   └── uploads/      ← Create this empty folder
└── frontend/
```

#### Step 2 — Download All Project Files

Place the backend files in the `backend/` folder:
- `app.py`
- `decrypt.py`
- `analyzer.py`
- `requirements.txt`

Place the frontend files in the `frontend/` folder:
- `index.html`
- `dashboard.html`
- `crypto.html`
- `style.css`

---

### PHASE 2 — Backend Setup

#### Step 3 — Open Command Prompt in Backend Folder

```
Method 1:
→ Go to your backend/ folder in File Explorer
→ Click the address bar at the top
→ Type: cmd
→ Press Enter
→ Command Prompt opens inside that folder ✅

Method 2:
→ Press Windows + R
→ Type: cmd
→ Navigate using: cd C:\path\to\whatsapp-forensics\backend
```

#### Step 4 — Install Required Libraries

Run this command (only needed once):

```bash
pip install -r requirements.txt
```

This installs:
- `flask` — web server framework
- `flask-cors` — allows browser to connect to Flask
- `pycryptodome` — AES-256-GCM decryption library

Expected output:
```
Successfully installed Flask-3.0.3 flask-cors-4.0.1 pycryptodome-3.20.0
```

#### Step 5 — Start the Flask Server

```bash
python app.py
```

You should see:

```
🔍 WhatsApp Forensics API
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Upload folder : C:\...\backend\uploads
   API running at: http://localhost:5000
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * Running on http://127.0.0.1:5000
 * Debug mode: on
Press CTRL+C to quit
```

✅ **Backend is running! Keep this window OPEN.**

#### Step 6 — Verify API is Working

Open your browser and go to:
```
http://localhost:5000
```

You should see:
```json
{
  "status": "online",
  "service": "WhatsApp Forensics API",
  "version": "1.0.0"
}
```

---

### PHASE 3 — Frontend Setup

#### Step 7 — Open the Upload Page

Go to your `frontend/` folder → **Double-click `index.html`**

The upload page opens in your browser automatically.

#### Step 8 — Check API Connection

Look at the top navigation bar. You should see:

```
⬤ API Online     ← Green badge means backend is connected ✅
```

If it shows `⬤ API Offline` → Go back to Step 5 and start Flask again.

---

### PHASE 4 — Running the Investigation

#### Step 9 — Get the Sample Files

For testing, use the provided sample files:
- `key` — The 256-bit AES encryption key file
- `msgstore.db.crypt14` — The encrypted WhatsApp database

Place both files somewhere accessible on your laptop.

#### Step 10 — Upload Files

On the upload page:

1. Click the **Key File** box → Navigate to and select the `key` file
2. Click the **.crypt14** box → Navigate to and select `msgstore.db.crypt14`
3. Both boxes should show green checkmarks ✅
4. Click the big **🔓 Decrypt & Analyze** button

#### Step 11 — Watch the Progress Bar

You will see the steps happening in real time:
```
📤 Uploading files to Flask API...    [=====>        ] 20%
🔓 Decrypting with AES-256-GCM...    [==========>   ] 40%
🔬 Analyzing SQLite database...      [===============] 70%
✅ Complete! Loading dashboard...    [===============] 95%
```

#### Step 12 — View the Dashboard

The dashboard opens automatically showing:

| Section | What You See |
|---------|-------------|
| **Stat Cards** | Total messages, contacts, sent, received |
| **SHA-256 Hashes** | Chain of Custody for all 3 files |
| **Bar Chart** | Top 5 most contacted numbers |
| **Doughnut Chart** | Sent vs Received ratio |
| **Line Chart** | Messages per day timeline |
| **Message Table** | All recovered messages with search |
| **Export Buttons** | Download JSON report or CSV |

#### Step 13 — View Cryptography Page

Click **🔐 Cryptography** in the navigation bar to see the full explanation of AES-256-GCM encryption.

---

## 📄 How Each File Works

### `app.py` — Main Flask Server

This is the heart of the backend. It:
- Creates the Flask web server on port 5000
- Defines API endpoints
- Receives uploaded files from the browser
- Calls `decrypt.py` and `analyzer.py`
- Returns JSON results to the frontend

```python
# Key endpoint
@app.route('/api/upload', methods=['POST'])
def upload_and_analyze():
    # 1. Receive files
    # 2. Save to uploads/
    # 3. Call decrypt_whatsapp_crypt14()
    # 4. Call analyze_database()
    # 5. Return JSON response
```

---

### `decrypt.py` — AES-256-GCM Decryption

This file contains the actual cryptographic decryption logic:

```python
from Crypto.Cipher import AES

# Step 1: Read 32-byte AES key from key file
key = key_data[30:62]           # Bytes 30 to 62

# Step 2: Read 16-byte IV from database header
iv = db_data[67:83]             # Bytes 67 to 83

# Step 3: Get encrypted content (after 190-byte header)
ciphertext = db_data[190:]      # From byte 190 onwards

# Step 4: Decrypt using AES-256-GCM
cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
decrypted = cipher.decrypt(ciphertext)

# Step 5: Verify - every SQLite file starts with "SQLite"
if decrypted[:6] == b'SQLite':
    print("Decryption successful!")
```

It also generates SHA-256 hashes:
```python
import hashlib
sha256 = hashlib.sha256()
with open(filepath, 'rb') as f:
    for chunk in iter(lambda: f.read(4096), b''):
        sha256.update(chunk)
return sha256.hexdigest()  # 64-character hex string
```

---

### `analyzer.py` — SQLite Database Reader

After decryption, this file reads all forensic artifacts:

```python
import sqlite3

conn = sqlite3.connect(decrypted_db_path)
cursor = conn.cursor()

# Read all messages
cursor.execute("""
    SELECT key_remote_jid, data, timestamp, key_from_me
    FROM messages
    ORDER BY timestamp DESC
    LIMIT 100
""")

# Convert timestamp to readable format
datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
```

It extracts:
- Total message count
- Sent vs received counts
- Top 5 most frequent contacts
- Daily message timeline
- All database table names

---

### `index.html` — Upload Page

The landing page where users upload files. Key features:
- **API health check** — automatically checks if Flask is running
- **File selection** — two drop zones for key and crypt14 files
- **Progress bar** — shows real-time decryption steps
- **Error handling** — shows helpful error messages

JavaScript function that triggers everything:
```javascript
async function startAnalysis() {
    const formData = new FormData();
    formData.append('key_file', keyFile);
    formData.append('crypt_file', cryptFile);

    const res = await fetch('http://localhost:5000/api/upload', {
        method: 'POST',
        body: formData
    });

    const data = await res.json();

    if (data.success) {
        localStorage.setItem('forensicResults', JSON.stringify(data));
        window.location.href = 'dashboard.html';  // Go to dashboard
    }
}
```

---

### `dashboard.html` — Evidence Dashboard

Displays all forensic findings. Key features:
- Loads data from `localStorage` (saved from upload page)
- Renders 3 Chart.js visualizations
- Builds searchable message table dynamically
- Clickable database table badges (with detailed popups)
- Export to JSON and CSV

---

### `crypto.html` — Cryptography Explanation

Educational page explaining:
- What encryption is (with plain vs encrypted examples)
- AES-256-GCM explained (each component)
- 5-step WhatsApp encryption flow
- Key cryptography terms glossary
- Why this matters for forensics

---

### `style.css` — Shared Styling

Single CSS file used by all 3 HTML pages. Contains:
- Color variables (white theme with green, blue, orange accents)
- Navigation styling
- Card and grid layouts
- Chart containers
- Message table styling
- Responsive mobile breakpoints

---

## 🔌 API Endpoints

### GET `/`
**Purpose:** Health check — verify server is running

**Response:**
```json
{
  "status": "online",
  "service": "WhatsApp Forensics API",
  "version": "1.0.0"
}
```

---

### GET `/api/status`
**Purpose:** Check server status and upload folder

**Response:**
```json
{
  "status": "running",
  "upload_folder": "C:\\...\\uploads",
  "files_stored": 3
}
```

---

### POST `/api/upload`
**Purpose:** Main forensic pipeline — decrypt and analyze

**Request:**
```
Content-Type: multipart/form-data
Body:
  key_file:   [binary key file]
  crypt_file: [binary .crypt14 file]
```

**Success Response:**
```json
{
  "success": true,
  "decryption": {
    "key_sha256":    "a3f1c2d4e5b6...",
    "crypt_sha256":  "b4c5d6e7f8a9...",
    "db_sha256":     "c5d6e7f8a9b0...",
    "db_size_bytes": 28672
  },
  "analysis": {
    "total_messages":  56,
    "total_contacts":  7,
    "sent_count":      28,
    "received_count":  28,
    "tables_found":    ["messages","chat_list","media_refs","receipts"],
    "messages":        [...],
    "top_contacts":    [...],
    "timeline":        [...]
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "stage":   "decryption",
  "error":   "Key and database do not match"
}
```

---

## 🔐 Cryptography Explained

### WhatsApp's Encryption Algorithm: AES-256-GCM

| Component | Meaning | Detail |
|-----------|---------|--------|
| **AES** | Advanced Encryption Standard | US Government standard since 2001 |
| **256** | Key size in bits | 32 bytes = 2²⁵⁶ possible keys |
| **GCM** | Galois/Counter Mode | Encrypts + verifies integrity |

### The .crypt14 File Structure

```
Byte Position    Content
──────────────────────────────────────────────────
Bytes 0-1      : Varint (header length = 188)
Bytes 2-189    : Protobuf header
  Bytes 13-45  : Key fingerprint (32 bytes)
  Bytes 67-83  : IV / Initialization Vector (16 bytes)
Bytes 190+     : Encrypted ciphertext (AES-256-GCM)
Last 16 bytes  : GCM Authentication Tag
──────────────────────────────────────────────────
```

### The Key File Structure

```
Byte Position    Content
──────────────────────────────────────────────────
Bytes 0-29     : Java serialization header
Bytes 30-61    : AES-256 key (32 bytes) ← We use this!
Bytes 62+      : Padding
──────────────────────────────────────────────────
```

### Decryption Formula

```
Key  = key_file[30:62]           → 32 bytes (256 bits)
IV   = crypt14_file[67:83]       → 16 bytes (128 bits)
Data = crypt14_file[190:]        → ciphertext + tag
─────────────────────────────────────────────────────
AES_GCM_DECRYPT(Key, IV, Data) = Plain SQLite Database
```

### SHA-256 Chain of Custody

```
BEFORE investigation:
  SHA256(key_file)    → "a3f1c2d4e5b6a7f8..."   (document this)
  SHA256(crypt14)     → "b4c5d6e7f8a9b0c1..."   (document this)

AFTER decryption:
  SHA256(decrypted)   → "c5d6e7f8a9b0c1d2..."   (document this)

If SHA256 values match at any future check → evidence is authentic ✅
If SHA256 values changed                  → evidence was tampered ❌
```

---

## 📦 Sample Data

The project includes sample files for testing:

| File | Size | Contents |
|------|------|---------|
| `key` | 158 bytes | AES-256 encryption key |
| `msgstore.db.crypt14` | ~29 KB | Encrypted database with 56 messages |

### What's Inside the Sample Database

```
7 unique Indian phone numbers:
  917845231096  → Friend (college chat)
  919632587410  → Classmate (project discussion)
  918754963201  → Family (Amma chat)
  916398274510  → Classmate (sharing notes)
  917412589630  → Friend (weekend plans)
  919087654321  → Friend (exam preparation)
  918563214790  → Friend (tech discussion)

4 database tables:
  messages    → 56 realistic conversations
  chat_list   → 7 contact entries
  media_refs  → 3 media file references
  receipts    → 2 read receipt records
```

---

## 📊 Dashboard Features

### 1. Stat Cards
Four cards showing key forensic metrics:
- **Total Messages** — recovered from database
- **Unique Contacts** — distinct phone numbers found
- **Sent by User** — outgoing messages (key_from_me = 1)
- **Received** — incoming messages (key_from_me = 0)

### 2. Chain of Custody Hashes
Three SHA-256 hash values displayed:
- Key file hash
- Encrypted database hash
- Decrypted database hash

### 3. Visual Charts (Chart.js)
- **Bar Chart** — Top 5 contacts by message count
- **Doughnut Chart** — Sent vs Received ratio
- **Line Chart** — Message activity by date

### 4. Database Tables Section
Clickable badges for each SQLite table found. Clicking opens a popup showing:
- Table description
- Column structure with data types
- Forensic importance

### 5. Message Table
Searchable table with columns:
- Serial number
- Contact JID (phone number)
- Message content
- UTC timestamp
- Direction badge (SENT / RECV)

### 6. Export Options
- **JSON Export** — Complete forensic report with all metadata
- **CSV Export** — Messages in spreadsheet format for documentation

---

## ▶️ How to Run the Project

### Every Time You Want to Run

```
STEP 1 → Open Command Prompt in backend/ folder
          cd C:\path\to\whatsapp-forensics\backend

STEP 2 → Start Flask server
          python app.py

STEP 3 → Open frontend in browser
          Double-click frontend/index.html

STEP 4 → Upload files and analyze
          Upload key + msgstore.db.crypt14
          Click Decrypt & Analyze

DONE! ✅
```

### What Should Be Open Simultaneously

| Window | Purpose |
|--------|---------|
| **Command Prompt** | Flask server running (never close!) |
| **Web Browser** | Frontend HTML pages |

---

## ❗ Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `API Offline` badge | Flask not running | Run `python app.py` in backend folder |
| `Module not found` | Libraries not installed | Run `pip install -r requirements.txt` |
| `Decryption failed` | Wrong files / mismatched key | Use the provided sample files |
| Charts not showing | No internet connection | Chart.js loads from CDN — need internet |
| Blank white page | style.css missing | Ensure all 4 files are in same frontend/ folder |
| Port already in use | Another app using 5000 | Close other programs and retry |
| `python` not found | Python not in PATH | Reinstall Python and check "Add to PATH" |

### Quick Health Check

```bash
# Check Python
python --version

# Check pip
pip --version

# Check libraries installed
pip show flask pycryptodome flask-cors

# Test API
curl http://localhost:5000
```

---

## ⚖️ Legal Disclaimer

```
⚠️  IMPORTANT LEGAL NOTICE

This project is developed STRICTLY for:
  ✅ Academic research and education
  ✅ Learning cryptography and digital forensics
  ✅ Analyzing files you own or have authorization for

This project must NOT be used for:
  ❌ Accessing someone else's WhatsApp without permission
  ❌ Unauthorized surveillance or monitoring
  ❌ Any illegal activity

Applicable Laws:
  India  → IT Act 2000, Section 43 and 66
  USA    → Computer Fraud and Abuse Act (CFAA)
  EU     → General Data Protection Regulation (GDPR)

Always obtain written legal authorization before
investigating any real device.
```

---

## 🔁 Project Flow Summary

```
┌─────────────────────────────────────────────┐
│              PROJECT FLOW                   │
│                                             │
│  USER                                       │
│    │                                        │
│    ▼                                        │
│  Upload Page (index.html)                   │
│    │  Selects key + .crypt14                │
│    │                                        │
│    ▼                                        │
│  HTTP POST → /api/upload                   │
│    │                                        │
│    ▼                                        │
│  Flask (app.py)                             │
│    │  Saves files                           │
│    │                                        │
│    ▼                                        │
│  decrypt.py                                 │
│    │  key[30:62]  = AES key                 │
│    │  db[67:83]   = IV                      │
│    │  db[190:]    = ciphertext              │
│    │  AES_GCM.decrypt() → SQLite DB        │
│    │                                        │
│    ▼                                        │
│  hashlib.sha256() → Chain of Custody       │
│    │                                        │
│    ▼                                        │
│  analyzer.py                                │
│    │  sqlite3.connect(db)                   │
│    │  SELECT messages, contacts, timeline   │
│    │                                        │
│    ▼                                        │
│  JSON Response                              │
│    │                                        │
│    ▼                                        │
│  Dashboard (dashboard.html)                 │
│    │  Stat cards                            │
│    │  SHA-256 hashes                        │
│    │  3 Charts (Chart.js)                   │
│    │  Message table + search               │
│    │  Export JSON / CSV                     │
│    │                                        │
│    ▼                                        │
│  Cryptography Page (crypto.html)           │
│       AES-256-GCM explanation               │
└─────────────────────────────────────────────┘
```

---

## 📚 References

- NIST AES Standard (FIPS 197) — nvlpubs.nist.gov
- NIST GCM Specification (SP 800-38D) — nvlpubs.nist.gov
- WhatsApp Security Whitepaper — scontent.whatsapp.net
- SQLite Database Format — sqlite.org/fileformat.html
- ISO/IEC 27037 — Digital Evidence Guidelines
- Android Debug Bridge (ADB) — developer.android.com

---

## 🎓 Academic Information

```
Project Title : Digital Forensics Investigation of WhatsApp
               on Android Devices
Domain        : Cybersecurity / Digital Forensics / Cryptography
Technology    : Python Flask + AES-256-GCM + SQLite + HTML/CSS/JS
Year          : 2024
```

---

*This project demonstrates real-world forensic techniques including
AES-256-GCM decryption, SHA-256 Chain of Custody, and SQLite
database forensics — all used by professional investigators worldwide.*
