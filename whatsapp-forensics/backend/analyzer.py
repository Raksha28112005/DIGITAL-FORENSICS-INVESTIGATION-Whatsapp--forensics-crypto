"""
analyzer.py - WhatsApp SQLite Database Forensic Analyzer
Digital Forensics Investigation Project
"""

import sqlite3
from datetime import datetime
from collections import Counter


def safe_timestamp(ts):
    """Convert WhatsApp timestamp (ms or s) to readable string."""
    try:
        ts = int(ts)
        if ts > 1e12:
            ts = ts // 1000   # Convert milliseconds to seconds
        return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S UTC')
    except Exception:
        return "Unknown"


def get_table_names(cursor):
    """List all tables in the database."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return [row[0] for row in cursor.fetchall()]


def analyze_database(db_path):
    """
    Perform full forensic analysis of a decrypted WhatsApp SQLite database.

    Args:
        db_path: Path to decrypted .db file

    Returns:
        dict with full forensic findings
    """
    result = {
        "success"        : False,
        "total_messages" : 0,
        "total_contacts" : 0,
        "sent_count"     : 0,
        "received_count" : 0,
        "media_count"    : 0,
        "tables_found"   : [],
        "messages"       : [],
        "top_contacts"   : [],
        "timeline"       : [],
        "error"          : None
    }

    try:
        conn   = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # --- Step 1: Discover tables ---
        result["tables_found"] = get_table_names(cursor)

        # --- Step 2: Check if messages table exists ---
        if 'messages' not in result["tables_found"]:
            raise ValueError(
                f"No 'messages' table found. Tables present: {result['tables_found']}"
            )

        # --- Step 3: Get column names dynamically ---
        cursor.execute("PRAGMA table_info(messages)")
        cols = [row[1] for row in cursor.fetchall()]

        # Pick the right column names (vary by WhatsApp version)
        contact_col = 'key_remote_jid'   if 'key_remote_jid'   in cols else (cols[1] if len(cols) > 1 else 'contact')
        msg_col     = 'data'             if 'data'             in cols else ('body' if 'body' in cols else cols[2] if len(cols) > 2 else 'message')
        ts_col      = 'timestamp'        if 'timestamp'        in cols else (cols[3] if len(cols) > 3 else 'timestamp')
        from_col    = 'key_from_me'      if 'key_from_me'      in cols else None
        media_col   = 'media_url'        if 'media_url'        in cols else None

        # --- Step 4: Total counts ---
        cursor.execute("SELECT COUNT(*) FROM messages")
        result["total_messages"] = cursor.fetchone()[0]

        if from_col:
            cursor.execute(f"SELECT COUNT(*) FROM messages WHERE {from_col}=1")
            result["sent_count"] = cursor.fetchone()[0]
            result["received_count"] = result["total_messages"] - result["sent_count"]

        if media_col:
            cursor.execute(f"SELECT COUNT(*) FROM messages WHERE {media_col} IS NOT NULL")
            result["media_count"] = cursor.fetchone()[0]

        # --- Step 5: Extract messages (latest 100) ---
        from_clause = f", {from_col}" if from_col else ""
        cursor.execute(f"""
            SELECT {contact_col}, {msg_col}, {ts_col}{from_clause}
            FROM messages
            ORDER BY {ts_col} DESC
            LIMIT 100
        """)
        rows = cursor.fetchall()

        for row in rows:
            sent = bool(row[3]) if from_col and len(row) > 3 else False
            result["messages"].append({
                "contact"    : str(row[0]) if row[0] else "Unknown",
                "message"    : str(row[1]) if row[1] else "[Media / Empty]",
                "timestamp"  : safe_timestamp(row[2]),
                "raw_ts"     : row[2],
                "sent_by_me" : sent
            })

        # --- Step 6: Top contacts ---
        contacts = [m["contact"] for m in result["messages"]]
        result["total_contacts"] = len(set(contacts))
        top = Counter(contacts).most_common(5)
        result["top_contacts"] = [{"contact": c, "count": n} for c, n in top]

        # --- Step 7: Timeline (messages per day) ---
        daily = {}
        for m in result["messages"]:
            day = m["timestamp"][:10] if m["timestamp"] != "Unknown" else "Unknown"
            daily[day] = daily.get(day, 0) + 1
        result["timeline"] = [
            {"date": d, "count": c}
            for d, c in sorted(daily.items())
        ]

        result["success"] = True
        conn.close()

    except Exception as e:
        result["error"] = str(e)

    return result
