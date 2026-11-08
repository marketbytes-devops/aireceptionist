import os
import sys

# Ensure project root is in sys.path so 'backend.app' imports work from any directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import uvicorn

if __name__ == "__main__":
    print(f"🌿 Starting AyurVoice SaaS backend on http://127.0.0.1:8000...")
    print(f"📖 Swagger Docs: http://127.0.0.1:8000/docs")
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)

