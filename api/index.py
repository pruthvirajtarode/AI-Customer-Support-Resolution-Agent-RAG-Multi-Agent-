import os
import sys
import traceback

# Monkeypatch sqlite3 for Vercel
try:
    import pysqlite3
    sys.modules["sqlite3"] = pysqlite3
except ImportError:
    pass

# Minimal FastAPI for initial diagnosis
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "python_version": sys.version,
        "sqlite3_version": "patched" if "sqlite3" in sys.modules and sys.modules["sqlite3"].__name__ == "pysqlite3" else "default",
        "env": {
            "OPENAI_KEY_SET": os.getenv("OPENAI_API_KEY") is not None,
            "DATABASE_URL": os.getenv("DATABASE_URL", "default")
        }
    }

try:
    from backend.main import app as real_app
    # Mount at root because backend.main routers already have /api prefix
    app.mount("/", real_app)
except Exception as e:
    error_trace = traceback.format_exc()
    @app.get("/api/error")
    async def error_report():
        return JSONResponse({"error": str(e), "traceback": error_trace}, status_code=500)
