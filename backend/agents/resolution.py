import os
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage
except ImportError:
    from langchain_community.chat_models import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage

def resolution_agent(ticket_text, retrieved, order_json="", initial_triage=None):
    evidence = "\n".join([r["text"] for r in retrieved])
    citations = [r["citation"] for r in retrieved]
    
    # Use triage info
    classification = initial_triage.get("classification", "other") if initial_triage else "other"
    if initial_triage and initial_triage.get("missing_info"):
        return {
            "classification": classification,
            "decision": "escalate",
            "rationale": f"Missing information: {', '.join(initial_triage['missing_info'])}",
            "explanation": f"I see you're asking about a {classification}. Could you please provide your {' and '.join(initial_triage['missing_info'])} so I can help you better?",
            "citations": [],
            "customer_response": f"I see you're asking about a {classification}. Could you please provide your {' and '.join(initial_triage['missing_info'])} so I can help you better?",
            "internal_notes": "Triage detected missing information."
        }
    
    # Check for API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and evidence.strip():
        try:
            chat = ChatOpenAI(temperature=0, openai_api_key=api_key)
            messages = [
                SystemMessage(content="You are a Resolution Agent. Use the following context and order data to decide on the customer ticket. Output: decision (approve/deny/escalate), classification, and customer-facing response."),
                HumanMessage(content=f"Policy Context: {evidence}\n\nOrder Data: {order_json}\n\nTicket: {ticket_text}")
            ]
            # Simple simulation of result parsing
            res = chat.invoke(messages).content
            return {
                "classification": classification,
                "decision": "approve" if "approve" in res.lower() else "deny" if "deny" in res.lower() else "escalate",
                "rationale": res[:200],
                "explanation": res,
                "citations": citations,
                "customer_response": res,
                "internal_notes": "AI generated."
            }
        except Exception:
            pass

    # Simple logic fallback: if no evidence found in policy
    if not evidence.strip():
        return {
            "classification": "other",
            "decision": "escalate",
            "rationale": "The current policy base does not contain information regarding this request.",
            "explanation": "I'm sorry, I couldn't find specific instructions in our current policy documents regarding this request.",
            "citations": [],
            "customer_response": "I'm sorry, I couldn't find specific instructions in our current policy documents regarding this request. I have escalated this to a human specialist.",
            "internal_notes": "No grounding found."
        }

    evidence_low = evidence.lower()
    ticket_low = ticket_text.lower()
    order_low = order_json.lower()
    
    if "refund" in ticket_low or "return" in ticket_low:
        if "perishable" in evidence_low or "food" in evidence_low or "food" in order_low:
            decision = "deny"
            rationale = "Policy explicitly prohibits refunds for perishable items/food."
        elif "final sale" in evidence_low or "final_sale" in order_low:
            decision = "deny"
            rationale = "Item is marked as final sale, which is non-refundable."
        elif "hygiene" in order_low:
             decision = "deny"
             rationale = "Hygiene products are not returnable for safety reasons."
        elif "software" in order_low and "opened" in ticket_low:
             decision = "deny"
             rationale = "Opened software cannot be returned."
        else:
            decision = "approve"
            rationale = "Request aligns with standard refund/return policy guidelines."
    elif "cancel" in ticket_low:
        if "shipped" in evidence_low or "transit" in evidence_low or "shipped" in order_low:
            decision = "deny"
            rationale = "Orders cannot be cancelled once they have been shipped."
        else:
            decision = "approve"
            rationale = "Order is eligible for cancellation as it has not yet shipped."
    else:
        decision = "escalate"
        rationale = "Manual review required for this complex case."

    return {
        "classification": classification,
        "decision": decision,
        "rationale": rationale,
        "explanation": f"Based on our policy: {rationale}",
        "citations": citations,
        "customer_response": f"Based on our policy: {rationale}",
        "internal_notes": "Processed by SupportAI Pipeline."
    }
