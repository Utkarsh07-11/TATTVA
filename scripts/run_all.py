"""Launch FastAPI and the Vite dev server (or the built UI if dist exists)."""

import os
import sys
import subprocess
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def main():
    print("SIH 2026 PS 26009: Manganese Decision Support Platform")
    venv_python = BASE_DIR / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        venv_python = Path(sys.executable)

    model_file = BASE_DIR / "data" / "models" / "production_forecaster.pkl"
    if not model_file.exists():
        subprocess.run([str(venv_python), str(BASE_DIR / "scripts" / "train_pipeline.py")], check=True)

    print("Starting FastAPI on http://127.0.0.1:8000 ...")
    backend_proc = subprocess.Popen(
        [str(venv_python), "-m", "uvicorn", "src.api.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(BASE_DIR),
    )
    time.sleep(2)

    frontend_dir = BASE_DIR / "frontend"
    dist_index = frontend_dir / "dist" / "index.html"
    frontend_proc = None
    if dist_index.exists():
        print("Built UI available at http://127.0.0.1:8000")
    else:
        print("Starting Vite frontend on http://localhost:5173 ...")
        frontend_proc = subprocess.Popen("npm run dev", cwd=str(frontend_dir), shell=True)

    print("API docs: http://127.0.0.1:8000/docs")
    print("Press Ctrl+C to stop.")
    try:
        backend_proc.wait()
        if frontend_proc:
            frontend_proc.wait()
    except KeyboardInterrupt:
        backend_proc.terminate()
        if frontend_proc:
            frontend_proc.terminate()


if __name__ == "__main__":
    main()
