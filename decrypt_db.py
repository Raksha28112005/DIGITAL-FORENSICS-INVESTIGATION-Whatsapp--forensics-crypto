from cryptography.fernet import Fernet

with open("key.key", "rb") as f:
    key = f.read()

cipher = Fernet(key)

with open("msgstore.db.enc", "rb") as f:
    encrypted = f.read()

decrypted = cipher.decrypt(encrypted)

with open("msgstore_decrypted.db", "wb") as f:
    f.write(decrypted)

print("Database decrypted")
