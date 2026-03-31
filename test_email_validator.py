from pydantic import BaseModel, EmailStr
import sys

class TestModel(BaseModel):
    email: EmailStr

try:
    m = TestModel(email="test@example.com")
    print("SUCCESS: email-validator is installed.")
except Exception as e:
    print(f"FAILURE: {e}")
    sys.exit(1)
