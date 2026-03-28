from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import init_db
from backend.routes import auth, policy, ticket, evaluation
from contextlib import asynccontextmanager

from fastapi.staticfiles import StaticFiles
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    init_db()
    yield

app = FastAPI(title="SupportAI SaaS", lifespan=lifespan)

# Routers (prefixed with /api for Consistency)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(policy.router, prefix="/api/policy", tags=["policy"])
app.include_router(ticket.router, prefix="/api/ticket", tags=["ticket"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["evaluation"])

# Serve frontend_html static files at root
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend_html")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")

@app.get("/api")
def root():
    return {"message": "SupportAI SaaS is running."}
