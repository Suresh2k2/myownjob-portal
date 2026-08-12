#!/usr/bin/env python3
"""Start the Job Portal API server. Run from backend/ directory."""
import os, sys, signal

os.environ.setdefault("SECRET_KEY", "dev-secret-key-change-in-production")
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app.main import app
import uvicorn

def shutdown(sig, frame):
    print("\nShutting down...")
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

print("Starting Job Portal API on http://localhost:8000")
print("Swagger UI: http://localhost:8000/docs")
print("Press Ctrl+C to stop\n")
uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
