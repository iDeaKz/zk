# start_chronomorph.py — Launches both API and GUI
import subprocess, threading, webbrowser, time
from uvicorn import run as run_api

def start_api():
    run_api("chrono_api:app", host="127.0.0.1", port=8000)

def start_gui():
    time.sleep(2)
    webbrowser.open("http://localhost:8501")
    subprocess.run(["streamlit", "run", "chrono_gui.py"])

if __name__ == "__main__":
    threading.Thread(target=start_api, daemon=True).start()
    start_gui()