import socket
import time

SERVER_IP = '127.0.0.1'
CLIENT_PORT = 5000

def start_client():
    print(f"[CLIENT] Connecting to Authentication Server at {SERVER_IP}:{CLIENT_PORT}...")
    
    while True:
        try:

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((SERVER_IP, CLIENT_PORT))
                print("[CLIENT] Connected successfully.")
                
                count = 1
                while True:
                    message = f"AUTH_REQUEST_{count}".encode()
                    sock.sendall(message)
                    data = sock.recv(1024)
                    
                    if not data:
                        print("[CLIENT] Server closed the connection.")
                        break
                        
                    print(f"[CLIENT] Server replied: {data.decode().strip()}")
                    count += 1
                    time.sleep(1)
                    
        except ConnectionRefusedError:
            print("[CLIENT] Connection refused. Is the server running?")
            time.sleep(2)
        except ConnectionResetError:
            print("\n[CLIENT] ERROR: Connection reset by peer! The server just crashed.")
            break
        except Exception as e:
            print(f"\n[CLIENT] Unexpected error: {e}")
            break

if __name__ == "__main__":
    start_client()