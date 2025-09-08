import subprocess
import sys
import os
import signal
import time


SERVICES = [
    {
        "name": "service_upload",
        "cmd": [sys.executable, "service_upload/main.py"],
        "port": 8001,
    },
    {
        "name": "service_trend",
        "cmd": [sys.executable, "service_trend/main.py"],
        "port": 8002,
    },
    {
        "name": "service_analysis",
        "cmd": [sys.executable, "service_analysis/main.py"],
        "port": 8003,
    },
    {
        "name": "service_generation",
        "cmd": [sys.executable, "service_generation/main.py"],
        "port": 8004,
    },
    {
        "name": "service_quality",
        "cmd": [sys.executable, "service_quality/main.py"],
        "port": 8005,
    },
    {
        "name": "service_ui",
        "cmd": [sys.executable, "-m", "streamlit", "run", "service_ui/app.py", "--server.headless=true", "--browser.gatherUsageStats=false"],
        "port": 8501,
    },
]


def main() -> None:
    processes = []

    env = os.environ.copy()
    # Example: set shared defaults here if needed
    # env.setdefault("PYTHONUNBUFFERED", "1")

    try:
        print("Starting services...")
        for svc in SERVICES:
            print(f"-> {svc['name']} on port {svc['port']} ...")
            p = subprocess.Popen(
                svc["cmd"],
                cwd=os.getcwd(),
                env=env,
            )
            processes.append((svc["name"], p))

        print("All processes launched. Press Ctrl+C to stop.")

        # Keep the parent alive while children run
        while True:
            time.sleep(1)
            # Optionally monitor child health here

    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        # Gracefully terminate all
        for name, p in processes:
            if p.poll() is None:
                try:
                    if os.name == "nt":
                        p.send_signal(signal.CTRL_BREAK_EVENT)
                    else:
                        p.terminate()
                except Exception:
                    pass

        # Give them a moment to exit
        time.sleep(2)
        for name, p in processes:
            if p.poll() is None:
                try:
                    p.kill()
                except Exception:
                    pass
        print("All services stopped.")


if __name__ == "__main__":
    main()


