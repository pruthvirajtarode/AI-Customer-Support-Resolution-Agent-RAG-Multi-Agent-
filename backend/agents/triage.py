import re
import os
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage
except ImportError:
    from langchain_community.chat_models import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage

def triage_agent(ticket_text):
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            chat = ChatOpenAI(temperature=0, openai_api_key=api_key)
            messages = [
                SystemMessage(content="You are a Triage Agent. Classify the customer ticket into: refund, shipping, cancellation, fraud, or other. Also identify missing information like order_id or date."),
                HumanMessage(content=ticket_text)
            ]
            res = chat.invoke(messages).content
            
            # Simple parsing for placeholder logic compatibility
            classification = "other"
            for cat in ["refund", "shipping", "cancellation", "fraud"]:
                if cat in res.lower():
                    classification = cat
                    break
            return {
                "classification": classification,
                "missing_info": ["order_id"] if "order" not in ticket_text.lower() else [],
                "clarifying_questions": [f"Could you provide more context?"]
            }
        except Exception:
            pass

    # Fallback to local logic
    categories = ["refund", "shipping", "cancellation", "fraud", "other"]
    classification = "other"
    for cat in categories:
        if cat in ticket_text.lower():
            classification = cat
            break
    missing = []
    if not re.search(r"order[ _]?id", ticket_text, re.I):
        missing.append("order_id")
    if not re.search(r"date", ticket_text, re.I):
        missing.append("date")
    return {
        "classification": classification,
        "missing_info": missing,
        "clarifying_questions": [f"Please provide {m}." for m in missing[:3]]
    }
