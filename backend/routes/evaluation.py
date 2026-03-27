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

@router.get("/report")
def evaluation_report(user: User = Depends(get_current_user)):
    results = []
    correct = 0
    citation_coverage = 0
    escalation_accuracy = 0
    for case in evaluation_cases:
        res = evaluate_case(case, user.id)
        expected = case["expected"]
        is_correct = (res["decision"] == expected["decision"]) and (res["classification"] == expected["classification"])
        correct += int(is_correct)
        citation_coverage += int(bool(res.get("citations")))
        escalation_accuracy += int(res["decision"] == "escalate" if expected["decision"] == "escalate" else 1)
        results.append({"input": case, "output": res, "correct": is_correct})
    total = len(evaluation_cases)
    report = {
        "total": total,
        "correctness": f"{correct}/{total}",
        "citation_coverage": f"{citation_coverage/total*100:.1f}%",
        "escalation_accuracy": f"{escalation_accuracy/total*100:.1f}%",
        "details": results
    }
    return report
