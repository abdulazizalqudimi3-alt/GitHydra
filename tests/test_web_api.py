import os
import time
import requests
import subprocess
import signal

def test_api_status():
    print("Starting GitHydra server for testing...")
    # Start server
    process = subprocess.Popen(
        ["python3", "-m", "githydra", "web", ".", "--port", "5002", "--no-browser"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    success = False
    try:
        # Wait for server to start
        for _ in range(15):
            time.sleep(1)
            try:
                response = requests.get("http://localhost:5002/api/git/status")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print("✅ API check successful!")
                        print(f"Current branch: {data['data']['branch']}")
                        success = True
                        break
            except requests.exceptions.ConnectionError:
                continue

        if not success:
            print("❌ API check failed or timed out.")

    finally:
        print("Stopping server...")
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)

    return success

if __name__ == "__main__":
    if test_api_status():
        exit(0)
    else:
        exit(1)
