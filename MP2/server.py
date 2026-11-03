import socket
import threading
import time
import random
import os
import json


SERVER_IP = '127.0.0.1'
CLIENT_PORT = 5000
MONITOR_PORT = 5001
HEARTBEAT_INTERVAL = 1.0
CHECKPOINT_FILE = "checkpoint.json"


state = {
    "total_authentications": 0
}

def save_checkpoint():

    while True:
        try:
            with open(CHECKPOINT_FILE, "w") as f:
                json.dump(state, f)
            time.sleep(0.5) 
        except Exception as e:
            print(f"[PRIMARY] Checkpoint error: {e}")
            break

def emit_heartbeats():

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        try:
            message = f"HEARTBEAT:{time.time()}".encode()
            udp_sock.sendto(message, (SERVER_IP, MONITOR_PORT))
            time.sleep(HEARTBEAT_INTERVAL)
        except Exception:
            break

def simulate_crash():

    lifespan = random.randint(10, 15)
    print(f"[PRIMARY] WARNING: Simulated crash arriving in {lifespan} seconds...")
    time.sleep(lifespan)
    print("\n[PRIMARY] FATAL ERROR: Segfault simulated! Process terminating.")
    os._exit(1)

def handle_client(conn, addr):

    print(f"[PRIMARY] Client connected from {addr}")
    global state
    with conn:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                

                state["total_authentications"] += 1
                current_auths = state["total_authentications"]
                
                print(f"[PRIMARY] Processed request. Total Auths: {current_auths}")
                response = f"AUTH_SUCCESS | Session Count: {current_auths}\n".encode()
                conn.sendall(response)
            except ConnectionResetError:
                break
    print(f"[PRIMARY] Client {addr} disconnected.")

def start_server():

    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"total_authentications": 0}, f)

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sock.bind((SERVER_IP, CLIENT_PORT))
    tcp_sock.listen()
    
    print(f"[PRIMARY] Authentication Service running on {SERVER_IP}:{CLIENT_PORT}")
    
    while True:
        conn, addr = tcp_sock.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        client_thread.start()

if __name__ == "__main__":
    threading.Thread(target=save_checkpoint, daemon=True).start()
    threading.Thread(target=emit_heartbeats, daemon=True).start()
    threading.Thread(target=simulate_crash, daemon=True).start()
    start_server()