import subprocess
import sys
import time
import os
import socket
from pathlib import Path

if sys.platform == "win32":
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.stderr and hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def is_port_open(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex((host, port)) == 0

def start_system():
    root_dir = str(Path(__file__).resolve().parent)
    env = os.environ.copy()
    env["PYTHONPATH"] = root_dir + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    
    print("=" * 65)
    print("🚀 Starting RAG-Based Document Intelligent System")
    print("   Reference: ACM TOIS 2026 (Ke et al., DOI: 10.1145/3768156)")
    print("=" * 65)
    
    backend_host = os.getenv("BACKEND_HOST", "127.0.0.1")
    backend_port = int(os.getenv("BACKEND_PORT", "8000"))
    frontend_port = int(os.getenv("FRONTEND_PORT", "8501"))

    # Check if ports are already taken
    if is_port_open(backend_port, backend_host):
        print(f"⚠️ Port {backend_port} is already in use. Please terminate existing process on {backend_port} or change port.")
    if is_port_open(frontend_port, "127.0.0.1"):
        print(f"⚠️ Port {frontend_port} is already in use. Please terminate existing process on {frontend_port} or change port.")
        
    # 1. Start FastAPI Backend in background process
    print(f"[1/2] Starting FastAPI Backend on http://{backend_host}:{backend_port}...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app.api.main:app", "--host", backend_host, "--port", str(backend_port)],
        env=env,
        cwd=root_dir
    )
    
    # Wait for backend to be ready
    for _ in range(20):
        if is_port_open(backend_port, "127.0.0.1"):
            break
        time.sleep(0.5)
        
    print(f" Backend online at http://127.0.0.1:{backend_port}")
    
    # 2. Start Streamlit Frontend
    print(f"[2/2] Starting Streamlit Frontend on http://localhost:{frontend_port}...")
    frontend_proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port", str(frontend_port), "--server.headless", "true"],
        env=env,
        cwd=root_dir
    )
    
    # Wait for frontend to be ready
    for _ in range(20):
        if is_port_open(frontend_port, "127.0.0.1"):
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
