"""
ChronoMorph Desktop Launcher
----------------------------
Boots the FastAPI backend and Streamlit GUI in sequence.
Includes error handling and logging for bootstrap diagnostics.
"""

import subprocess
import threading
import time
import traceback
from uvicorn import run as serve_api

def launch_api():
    """Launch FastAPI app on localhost:8000. Catches and logs any import/bootstrap errors."""
    try:
        serve_api("chrono_api:app", host="127.0.0.1", port=8000)
    except Exception as e:
        print("❌ API failed to launch:")
        traceback.print_exc()

def launch_gui():
    """Launch Streamlit GUI for agent interface."""
    time.sleep(2)
    try:
        subprocess.run(["streamlit", "run", "chrono_gui.py"])
    except Exception as e:
        print("❌ GUI failed to launch:")
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Launching ChronoMorph Desktop Interface...")
    threading.Thread(target=launch_api, daemon=True).start()
    launch_gui()# app_desktop.py — Desktop Wrapper for ChronoMorph Core
import subprocess, threading, time
from uvicorn import run as serve_api

def launch_api():
    serve_api("chrono_api:app", host="127.0.0.1", port=8000)

def launch_gui():
    time.sleep(2)
    subprocess.run(["streamlit", "run", "chrono_gui.py"])

if __name__ == "__main__":
    threading.Thread(target=launch_api, daemon=True).start()
    launch_gui()