import socket
import time
from datetime import datetime
import subprocess

MONITOR_IP = '127.0.0.1'
MONITOR_PORT = 5001
TIMEOUT_THRESHOLD = 3.0  

def log_incident(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("monitor_incident.log", "a") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")

def start_monitor():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind((MONITOR_IP, MONITOR_PORT))
    udp_sock.settimeout(1.0) 
    
    print(f"[MONITOR] Listening for heartbeats on {MONITOR_IP}:{MONITOR_PORT}...")
    
    last_heartbeat_time = time.time()
    server_alive = False
    failover_triggered = False

    while True:
        try:
            data, addr = udp_sock.recvfrom(1024)
            current_time = time.time()
            
            if not server_alive:
                print(f"[MONITOR] {datetime.now().strftime('%H:%M:%S')} - Heartbeat received. Node is ONLINE.")
                server_alive = True
                
            last_heartbeat_time = current_time
            
        except socket.timeout:
            time_since_last_beat = time.time() - last_heartbeat_time
            
            if server_alive and time_since_last_beat > TIMEOUT_THRESHOLD:
                timestamp = datetime.now().strftime("%H:%M:%S")
                alert_msg = f"CRITICAL ALERT: Primary crash detected! No heartbeat for {time_since_last_beat:.1f} seconds."
                print(f"\n[MONITOR] {timestamp} - {alert_msg}")
                log_incident(alert_msg)

                if not failover_triggered:
                    print(f"[MONITOR] {timestamp} - INITIATING AUTOMATED FAILOVER...")
                    log_incident("INITIATING AUTOMATED FAILOVER...")
                    
                    try:
                        subprocess.Popen(["python3", "replica.py"])
                        print(f"[MONITOR] {timestamp} - Failover successful! Standby node promoted.")
                        log_incident("Failover successful! Standby node promoted.")
                        failover_triggered = True
                    except Exception as e:
                        print(f"[MONITOR] FAILOVER ERROR: Could not launch replica.py: {e}")
                
                server_alive = False 

if __name__ == "__main__":
    start_monitor()