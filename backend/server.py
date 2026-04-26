"""
SeraNova AI — ASGI entry (FastAPI).

- Development:  python server.py
- Production:   gunicorn server:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --workers 2 --timeout 120

The `app` object is the same FastAPI application defined in fastapi_server.py.
"""
from __future__ import annotations

from fastapi_server import app

__all__ = ["app"]


if __name__ == "__main__":
    import os

    import uvicorn

    from config import Config

    port = int(os.environ.get("PORT", Config.PORT))
    host = os.environ.get("HOST", Config.HOST)
    reload = os.environ.get("FLASK_DEBUG", str(Config.FLASK_DEBUG)).lower() == "true"
    uvicorn.run("fastapi_server:app", host=host, port=port, reload=reload)
