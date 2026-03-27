import re

def triage_agent(ticket_text):
    categories = ["refund", "shipping", "cancellation", "fraud", "other"]
    classification = "other"
    for cat in categories:
        if cat in ticket_text.lower():
            classification = cat
            break
    # Identify missing info (simple heuristics)
    missing = []
    if not re.search(r"order[ _]?id", ticket_text, re.I):
        missing.append("order_id")
    if not re.search(r"date", ticket_text, re.I):
        missing.append("date")
    clarifying_questions = []
    if missing:
        for m in missing:
            clarifying_questions.append(f"Please provide {m}.")
    return {
        "classification": classification,
        "missing_info": missing,
        "clarifying_questions": clarifying_questions[:3]
    }
