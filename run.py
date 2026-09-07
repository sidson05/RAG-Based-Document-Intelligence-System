import subprocess
import sys
import time
import os
import socket
from pathlib import Path

def is_port_open(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex((host, port)) == 0

def start_system():
    root_dir = str(Path(__file__).resolve().parent)
    env = os.environ.copy()
    env["PYTHONPATH"] = root_dir + os.pathsep + env.get("PYTHONPATH", "")
    
    print("=" * 65)
    print("🚀 Starting RAG-Based Document Intelligent System")
    print("   Reference: ACM TOIS 2026 (Ke et al., DOI: 10.1145/3768156)")
    print("=" * 65)
    
    # Check if ports are already taken
    if is_port_open(8000):
        print("⚠️ Port 8000 is already in use. Please terminate existing process on 8000 or change port.")
    if is_port_open(8501):
        print("⚠️ Port 8501 is already in use. Please terminate existing process on 8501 or change port.")
        
    # 1. Start FastAPI Backend in background process
    print("[1/2] Starting FastAPI Backend on http://127.0.0.1:8000...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app.api.main:app", "--host", "127.0.0.1", "--port", "8000"],
        env=env,
        cwd=root_dir
    )
    
    # Wait for backend to be ready
    for _ in range(20):
        if is_port_open(8000):
            break
        time.sleep(0.5)
        
    print(" Backend online at http://127.0.0.1:8000")
    
    # 2. Start Streamlit Frontend
    print("[2/2] Starting Streamlit Frontend on http://localhost:8501...")
    frontend_proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8501", "--server.headless", "true"],
        env=env,
        cwd=root_dir
    )
    
    # Wait for frontend to be ready
    for _ in range(20):
        if is_port_open(8501):
            break
        time.sleep(0.5)
        
    print("\n System running successfully!")
    print("   - Web UI:       http://localhost:8501")
    print("   - API Docs:     http://127.0.0.1:8000/docs")
    print("\nKeep this window open. Press Ctrl+C to stop both servers.\n")
    
    try:
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping servers...")
        frontend_proc.terminate()
        backend_proc.terminate()
        print("Servers stopped.")

if __name__ == "__main__":
    start_system()
