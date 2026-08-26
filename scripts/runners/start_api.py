"""Start FastAPI ASGI Server with proper Python paths."""
import os
import sys
import uvicorn

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, ".pipdeps"))

from marketvoice.api.application import create_app

app = create_app()

if __name__ == "__main__":
    print(">> Launching MarketVoice SEA FastAPI Microservice on http://127.0.0.1:8000 ...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
