from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import init_db
from backend.routes import auth, policy, ticket, evaluation

app = FastAPI(title="SupportAI SaaS")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB
init_db()

# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(policy.router, prefix="/policy", tags=["policy"])
app.include_router(ticket.router, prefix="/ticket", tags=["ticket"])
app.include_router(evaluation.router, prefix="/evaluation", tags=["evaluation"])

@app.get("/")
def root():
    return {"message": "SupportAI SaaS is running."}
