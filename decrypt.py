from cryptography.fernet import Fernet

# Load the key used by the keylogger
with open("key.key", "rb") as f:
    key = f.read()

fernet = Fernet(key)

# Decrypt each line in the log
with open("encrypted_log.txt", "rb") as f:
    for line in f:
        try:
            decrypted = fernet.decrypt(line.strip()).decode()
            print(decrypted)
        except Exception as e:
            print(f"[!] Failed to decrypt line: {e}")
