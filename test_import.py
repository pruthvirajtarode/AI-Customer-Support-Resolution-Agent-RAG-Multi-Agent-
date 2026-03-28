import traceback
import sys
import os

try:
    print("Attempting to import backend.main.app...")
    from backend.main import app
    print("SUCCESS: App imported.")
except Exception as e:
    print(f"FAILED: {e}")
    traceback.print_exc()
