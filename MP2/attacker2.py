import json
import socket
import time

print("=== MP1.2 ADVERSARIAL AUDIT ===")

print("\n[ATTACK 2] Attempting to tamper with Checkpoint state...")
try:
    with open("checkpoint.json", "w") as f:
        json.dump({"total_authentications": 999999, "hacked_by_auditor": True}, f)
    print("[AUDITOR] SUCCESS: Injected poisoned state into checkpoint.json!")
    print("[AUDITOR] If the primary crashes now, the replica will load this poisoned state.")
except Exception as e:
    print(f"[AUDITOR] Failed to tamper with checkpoint: {e}")

time.sleep(2)

print("\n[ATTACK 1] Simulating False Failover (Network Delay)...")
print("[AUDITOR] Attempting to bind to the Primary's port (5000) while it is still alive...")
try:
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.bind(('127.0.0.1', 5000))
    print("[AUDITOR] DANGER: Split-Brain successful! Two primaries are now running.")
except OSError as e:
    print(f"[AUDITOR] DEFENDED: Split-Brain prevented! The Operating System blocked the port takeover.")
    print(f"[AUDITOR] Error received: {e}")

print("\n=== AUDIT COMPLETE ===")