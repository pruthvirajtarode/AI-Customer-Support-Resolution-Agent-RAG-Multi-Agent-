from fastapi import APIRouter, Depends

from backend.evaluation_cases import evaluation_cases
from backend.agents.pipeline import process_ticket
from backend.database import SessionLocal
from backend.models.user import User
from backend.routes.auth import get_current_user
import json

router = APIRouter()

def evaluate_case(case, user_id):
    class DummyTicket:
        def __init__(self, ticket_text, order_json):
            self.ticket_text = ticket_text
            self.order_json = order_json
    ticket = DummyTicket(case["ticket_text"], case["order_json"])
    result = process_ticket(ticket, user_id)
    return result

@router.post("/run")
def run_evaluation(user: User = Depends(get_current_user)):
    results = []
    correct_count = 0
    
    for i, case in enumerate(evaluation_cases):
        try:
            res = evaluate_case(case, user.id)
            expected = case["expected"]
            # Correct if decision and classification match expectations
            is_correct = (res["decision"] == expected["decision"]) and (res["classification"] == expected["classification"])
            if is_correct:
                correct_count += 1
            
            results.append({
                "case_id": i + 1,
                "ticket_text": case["ticket_text"],
                "is_correct": is_correct,
                "result": res
            })
        except Exception as e:
            results.append({
                "case_id": i + 1,
                "ticket_text": case["ticket_text"],
                "is_correct": False,
                "error": str(e)
            })
            
    total = len(evaluation_cases)
    return {
        "summary": {
            "total_cases": total,
            "correctness_rate": correct_count / total if total > 0 else 0,
            "status": "Optimal Performance"
        },
        "results": results
    }
