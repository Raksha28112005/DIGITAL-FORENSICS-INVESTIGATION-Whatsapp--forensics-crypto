import sqlite3

conn = sqlite3.connect("msgstore.db")
cursor = conn.cursor()

# Drop table if it already exists
cursor.execute("DROP TABLE IF EXISTS messages")

# Create messages table
cursor.execute("""
CREATE TABLE messages (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    receiver TEXT,
    message TEXT,
    message_type TEXT,
    timestamp TEXT
)
""")

# Insert multiple demo messages
messages = [
    ("Raksha", "Friend1", "Hello!", "text", "2026-02-17 09:00:00"),
    ("Friend1", "Raksha", "Hi Raksha 😊", "text", "2026-02-17 09:01:10"),
    ("Raksha", "Friend1", "How are you?", "text", "2026-02-17 09:02:00"),
    ("Friend1", "Raksha", "I'm fine, what about you?", "text", "2026-02-17 09:02:45"),

    ("Raksha", "Friend2", "Meeting at 5 PM", "text", "2026-02-17 10:15:00"),
    ("Friend2", "Raksha", "Okay 👍", "text", "2026-02-17 10:15:30"),

    ("Raksha", "Friend1", "photo_001.jpg", "image", "2026-02-17 11:00:00"),
    ("Friend1", "Raksha", "Nice photo!", "text", "2026-02-17 11:01:00"),

    ("Raksha", "Friend3", "Location shared", "location", "2026-02-17 12:30:00"),
    ("Friend3", "Raksha", "I reached", "text", "2026-02-17 12:45:00"),

    ("Raksha", "Friend1", "Call duration: 5 min", "call", "2026-02-17 14:00:00")
]

cursor.executemany("""
INSERT INTO messages (sender, receiver, message, message_type, timestamp)
VALUES (?, ?, ?, ?, ?)
""", messages)

conn.commit()
conn.close()

print("msgstore.db recreated successfully with multiple records")
