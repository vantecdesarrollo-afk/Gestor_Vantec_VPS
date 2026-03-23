import os
import subprocess

def restart_uvicorn():
    try:
        # Find PID using port 8000
        res = subprocess.check_output("netstat -ano | findstr 8000", shell=True).decode()
        print(f"Netstat output:\n{res}")
        pids = []
        for line in res.strip().split("\n"):
            if "LISTENING" in line:
                 parts = line.split()
                 pid = parts[-1]
                 pids.append(pid)
                 
        if pids:
             pid_to_kill = pids[0]
             print(f"Killing PID: {pid_to_kill}")
             subprocess.run(f"taskkill /F /PID {pid_to_kill} /T", shell=True)
             print("Uvicorn process killed.")
        else:
             print("No active listener on port 8000 found.")

    except Exception as e:
        print(f"Error finding/killing process: {e}")

if __name__ == "__main__":
    restart_uvicorn()
