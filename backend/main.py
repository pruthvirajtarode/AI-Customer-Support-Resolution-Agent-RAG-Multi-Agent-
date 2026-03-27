from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import init_db
from backend.routes import auth, policy, ticket, evaluation
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    init_db()
    yield

app = FastAPI(title="SupportAI SaaS", lifespan=lifespan)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers (prefixed with /api for Vercel/Production)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(policy.router, prefix="/api/policy", tags=["policy"])
app.include_router(ticket.router, prefix="/api/ticket", tags=["ticket"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["evaluation"])

@app.get("/")
def root():
    return {"message": "SupportAI SaaS is running."}
