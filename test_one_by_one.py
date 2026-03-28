import sys
import os

print("--- System Import Test ---")
try:
    print("Importing backend.database...")
    import backend.database
    print("OK")
    print("Importing backend.routes.auth...")
    import backend.routes.auth
    print("OK")
    print("Importing backend.routes.policy...")
    import backend.routes.policy
    print("OK")
    print("Importing backend.routes.ticket...")
    import backend.routes.ticket
    print("OK")
    print("Importing backend.routes.evaluation...")
    import backend.routes.evaluation
    print("OK")
    print("Importing backend.main...")
    import backend.main
    print("OK")
except Exception as e:
    print(f"FAILED on {e}")
    import traceback
    traceback.print_exc()
