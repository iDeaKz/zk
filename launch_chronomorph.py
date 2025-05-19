"""
launch_chronomorph.py

Unified launcher for ChronoMorph Visual Cognitive Storytelling Engine.
This script starts both the FastAPI backend and Streamlit frontend.
"""

import subprocess
import threading
import os
import time
import sys
import argparse
import logging
import signal
import atexit

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ChronoMorph")

# Global variables to track processes
api_process = None
streamlit_process = None

def clean_exit(signum=None, frame=None):
    """Cleanup function to terminate all processes on exit"""
    logger.info("Shutting down ChronoMorph...")
    
    if api_process:
        logger.info("Terminating API process...")
        try:
            api_process.terminate()
            api_process.wait(timeout=5)
        except:
            api_process.kill()
            
    if streamlit_process:
        logger.info("Terminating Streamlit process...")
        try:
            streamlit_process.terminate()
            streamlit_process.wait(timeout=5)
        except:
            streamlit_process.kill()
            
    logger.info("Shutdown complete.")
    sys.exit(0)

# Register the cleanup function
atexit.register(clean_exit)
signal.signal(signal.SIGINT, clean_exit)
signal.signal(signal.SIGTERM, clean_exit)

def start_api_server(host="0.0.0.0", port=8000, debug=False):
    """Start the FastAPI backend"""
    global api_process
    
    logger.info(f"Starting FastAPI backend on http://{host}:{port}")
    cmd = [sys.executable, "-m", "uvicorn", "chrono_api:app", "--host", host, "--port", str(port)]
    
    if debug:
        cmd.append("--reload")
        
    try:
        api_process = subprocess.Popen(cmd)
        logger.info("FastAPI backend started.")
        return True
    except Exception as e:
        logger.error(f"Failed to start FastAPI backend: {e}")
        return False

def start_streamlit(host="0.0.0.0", port=5000, debug=False):
    """Start the Streamlit frontend"""
    global streamlit_process
    
    logger.info(f"Starting Streamlit frontend on http://{host}:{port}")
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", str(port), "--server.address", host]
    
    try:
        streamlit_process = subprocess.Popen(cmd)
        logger.info("Streamlit frontend started.")
        return True
    except Exception as e:
        logger.error(f"Failed to start Streamlit frontend: {e}")
        return False
        
def check_directories():
    """Create required directories if they don't exist"""
    dirs = [
        "data/agents",
        "data/memory",
        "data/exports",
        "audio_themes",
        "temp"
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        logger.debug(f"Directory ensured: {dir_path}")

def launch_chronomorph(api_host="0.0.0.0", api_port=8000, 
                      streamlit_host="0.0.0.0", streamlit_port=5000,
                      debug=False):
    """Launch the complete ChronoMorph application"""
    logger.info("Launching ChronoMorph Vault...")
    
    # Ensure directories exist
    check_directories()
    
    # Start FastAPI backend
    api_success = start_api_server(api_host, api_port, debug)
    if not api_success:
        logger.error("Failed to start API. Exiting.")
        sys.exit(1)
    
    # Give API time to start
    time.sleep(3)
    
    # Start Streamlit frontend
    streamlit_success = start_streamlit(streamlit_host, streamlit_port, debug)
    if not streamlit_success:
        logger.error("Failed to start Streamlit. Exiting.")
        clean_exit()
        sys.exit(1)
    
    logger.info(f"""
    🚀 ChronoMorph Vault is now running:
    
    API: http://{api_host}:{api_port}
    UI:  http://{streamlit_host}:{streamlit_port}
    
    Press Ctrl+C to stop all services
    """)
    
    # Keep the main thread alive
    try:
        while True:
            # Check if processes are still alive
            if api_process.poll() is not None:
                logger.error("API process has terminated unexpectedly")
                break
                
            if streamlit_process.poll() is not None:
                logger.error("Streamlit process has terminated unexpectedly")
                break
                
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        clean_exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ChronoMorph Vault Launcher')
    parser.add_argument('--api-host', default='0.0.0.0', help='API hostname')
    parser.add_argument('--api-port', type=int, default=8000, help='API port')
    parser.add_argument('--ui-host', default='0.0.0.0', help='Streamlit hostname')
    parser.add_argument('--ui-port', type=int, default=5000, help='Streamlit port')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    print("""
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║           ChronoMorph Visual Cognitive           ║
    ║               Storytelling Engine                ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
    """)
    
    launch_chronomorph(
        api_host=args.api_host,
        api_port=args.api_port,
        streamlit_host=args.ui_host,
        streamlit_port=args.ui_port,
        debug=args.debug
    )