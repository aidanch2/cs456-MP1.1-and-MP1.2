import socket
import threading
import time
import random
import os


SERVER_IP = '127.0.0.1'
CLIENT_PORT = 5000
MONITOR_PORT = 5001
HEARTBEAT_INTERVAL = 1.0 

def emit_heartbeats():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        try:
            message = f"HEARTBEAT:{time.time()}".encode()
            udp_sock.sendto(message, (SERVER_IP, MONITOR_PORT))
            print("[SERVER] Heartbeat sent.")
            time.sleep(HEARTBEAT_INTERVAL)
        except Exception as e:
            print(f"[SERVER] Heartbeat error: {e}")
            break

def simulate_crash():

    lifespan = random.randint(10, 25)
    print(f"[SERVER] WARNING: Server will experience a simulated crash in {lifespan} seconds...")
    time.sleep(lifespan)
    print("\n[SERVER] FATAL ERROR: Simulated unpredictable crash occurred! Terminating immediately.")
    os._exit(1)

def handle_client(conn, addr):

    print(f"[SERVER] Client connected from {addr}")
    with conn:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"[SERVER] Received request: {data.decode().strip()}")
                response = "AUTH_SUCCESS\n".encode()
                conn.sendall(response)
            except ConnectionResetError:
                break
    print(f"[SERVER] Client {addr} disconnected.")

def start_server():

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sock.bind((SERVER_IP, CLIENT_PORT))
    tcp_sock.listen()
    
    print(f"[SERVER] Authentication Service running on {SERVER_IP}:{CLIENT_PORT}")
    
    while True:
        conn, addr = tcp_sock.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        client_thread.start()

if __name__ == "__main__":

    threading.Thread(target=emit_heartbeats, daemon=True).start()
    
    threading.Thread(target=simulate_crash, daemon=True).start()

    start_server()