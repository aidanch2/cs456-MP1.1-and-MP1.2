import socket
import threading
import time
import json
import os

SERVER_IP = '127.0.0.1'
CLIENT_PORT = 5000
MONITOR_PORT = 5001
HEARTBEAT_INTERVAL = 1.0
CHECKPOINT_FILE = "checkpoint.json"

state = {"total_authentications": 0}

def load_checkpoint():

    global state
    try:
        if os.path.exists(CHECKPOINT_FILE):
            with open(CHECKPOINT_FILE, "r") as f:
                state = json.load(f)
            print(f"[REPLICA] Checkpoint loaded successfully. Resuming at {state['total_authentications']} authentications.")
        else:
            print("[REPLICA] No checkpoint found. Starting from 0.")
    except Exception as e:
        print(f"[REPLICA] Error loading checkpoint: {e}")

def emit_heartbeats():

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        try:
            message = f"HEARTBEAT:{time.time()}".encode()
            udp_sock.sendto(message, (SERVER_IP, MONITOR_PORT))
            time.sleep(HEARTBEAT_INTERVAL)
        except Exception:
            break

def handle_client(conn, addr):

    print(f"[REPLICA] Client connected from {addr}")
    global state
    with conn:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                

                state["total_authentications"] += 1
                current_auths = state["total_authentications"]
                
                print(f"[REPLICA] Processed request. Total Auths: {current_auths}")
                
                response = f"AUTH_SUCCESS | Session Count: {current_auths} (SERVED BY REPLICA)\n".encode()
                conn.sendall(response)
            except ConnectionResetError:
                break
    print(f"[REPLICA] Client {addr} disconnected.")

def start_replica():

    load_checkpoint()
    time.sleep(1.0)
    
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        tcp_sock.bind((SERVER_IP, CLIENT_PORT))
        tcp_sock.listen()
        print(f"[REPLICA] Backup Service taking over on {SERVER_IP}:{CLIENT_PORT}")
        
        threading.Thread(target=emit_heartbeats, daemon=True).start()
        
        while True:
            conn, addr = tcp_sock.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            client_thread.start()
    except OSError as e:
        print(f"[REPLICA] FATAL: Could not bind to port. Is the primary still running? Error: {e}")

if __name__ == "__main__":
    print("[REPLICA] Promotion signal received! Spinning up secondary node...")
    start_replica()