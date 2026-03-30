from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import init_db
from backend.routes import auth, policy, ticket, evaluation


from fastapi.staticfiles import StaticFiles
import os

# Database initialization check
_db_initialized = False

def ensure_db():
    global _db_initialized
    if not _db_initialized:
        init_db()
        _db_initialized = True

# Initial check for Vercel
if os.getenv("VERCEL"):
    ensure_db()
else:
    init_db()

app = FastAPI(title="SupportAI SaaS")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers (prefixed with /api for Consistency)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(policy.router, prefix="/api/policy", tags=["policy"])
app.include_router(ticket.router, prefix="/api/ticket", tags=["ticket"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["evaluation"])

from fastapi.responses import FileResponse, JSONResponse

@app.get("/")
def serve_ui():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Vercel bundled path is api/static
    for folder in [os.path.join("api", "static"), "dist", "public"]:
        path = os.path.join(root, folder, "index.html")
        if os.path.exists(path):
            return FileResponse(path)
    return JSONResponse(content={"detail": "UI files not found in api/static. Deployment sync in progress."}, status_code=404)

@app.get("/api")
def api_root():
    return {"message": "SupportAI SaaS is running."}

# Serve public static files at root
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frontend_dir = os.path.join(root, "api", "static")
if not os.path.exists(frontend_dir):
    frontend_dir = os.path.join(root, "public") # Fallback

if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
