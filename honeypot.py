import socket
import threading
import logging
from datetime import datetime
import json
import os
import requests
from collections import defaultdict

# === CONFIGURATION ===
HOST = "0.0.0.0"     # Listen on all interfaces
PORT = 2222          # Fake SSH or FTP port
LOG_FILE = "honeypot_logs.json"
FAILED_THRESHOLD = 5

# === IP Tracking ===
ip_attempts = defaultdict(int)

# === Setup Logging ===
logging.basicConfig(filename="honeypot.log", level=logging.INFO, format='%(asctime)s - %(message)s')

# === Function: Get IP Info (Geolocation) ===
def get_ip_info(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}").json()
        return {
            "ip": ip,
            "country": res.get("country"),
            "region": res.get("regionName"),
            "city": res.get("city"),
            "org": res.get("org"),
            "lat": res.get("lat"),
            "lon": res.get("lon")
        }
    except:
        return {"ip": ip, "info": "Failed to fetch geo info"}

# === Function: Save Logs ===
def log_attempt(ip, username, password):
    info = {
        "timestamp": str(datetime.now()),
        "ip": ip,
        "username": username,
        "password": password,
        "geo": get_ip_info(ip)
    }
    logging.info(json.dumps(info))
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(info) + "\n")

# === Function: Block via fail2ban (manual integration) ===
def block_ip(ip):
    os.system(f"sudo fail2ban-client set sshd banip {ip}")

# === Client Handler ===
def handle_client(client_socket, addr):
    ip = addr[0]
    ip_attempts[ip] += 1

    try:
        client_socket.sendall(b"Welcome to Fake SSH Service\nUsername: ")
        username = client_socket.recv(1024).strip().decode(errors='ignore')
        client_socket.sendall(b"Password: ")
        password = client_socket.recv(1024).strip().decode(errors='ignore')

        log_attempt(ip, username, password)

        client_socket.sendall(b"Access Denied.\n")
        client_socket.close()

        if ip_attempts[ip] >= FAILED_THRESHOLD:
            print(f"[!] IP {ip} exceeded threshold. Recommend blocking.")
            # block_ip(ip)  # Uncomment if fail2ban is integrated manually

    except Exception as e:
        print(f"[!] Error with {ip}: {e}")
        client_socket.close()

# === Server Loop ===
def start_honeypot():
    print(f"[*] Starting Honeypot on port {PORT}...")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(100)

    while True:
        client_sock, addr = server.accept()
        print(f"[+] Connection from {addr[0]}")
        threading.Thread(target=handle_client, args=(client_sock, addr)).start()

# === Main ===
if __name__ == "__main__":
    start_honeypot()