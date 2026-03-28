import uvicorn
import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

from backend.main import app

if __name__ == "__main__":
    print("Starting SupportAI SaaS Server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
