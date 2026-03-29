import os
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage
except ImportError:
    from langchain_community.chat_models import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage

def resolution_agent(ticket_text, retrieved):
    evidence = "\n".join([r["text"] for r in retrieved])
    citations = [r["citation"] for r in retrieved]
    
    # Check for API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and evidence.strip():
        try:
            chat = ChatOpenAI(temperature=0, openai_api_key=api_key)
            messages = [
                SystemMessage(content="You are a Resolution Agent. Use the following context to decide on the customer ticket. Output: decision (approve/deny/escalate), classification, and customer-facing response."),
                HumanMessage(content=f"Context: {evidence}\n\nTicket: {ticket_text}")
            ]
            # Simple simulation of result parsing
            res = chat.invoke(messages).content
            return {
                "classification": "refund" if "refund" in ticket_text.lower() else "other",
                "decision": "approve" if "approve" in res.lower() else "deny" if "deny" in res.lower() else "escalate",
                "rationale": res[:200],
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
            "citations": [],
            "customer_response": "I'm sorry, I couldn't find specific instructions in our current policy documents regarding this request. I have escalated this to a human specialist.",
            "internal_notes": "No grounding found."
        }

    evidence_low = evidence.lower()
    ticket_low = ticket_text.lower()
    
    if "refund" in ticket_low or "return" in ticket_low:
        if "perishable" in evidence_low or "food" in evidence_low:
            decision = "deny"
            rationale = "Policy explicitly prohibits refunds for perishable items/food."
        elif "final sale" in evidence_low:
            decision = "deny"
            rationale = "Item is marked as final sale, which is non-refundable."
        else:
            decision = "approve"
            rationale = "Request aligns with standard refund/return policy guidelines."
    elif "cancel" in ticket_low:
        if "shipped" in evidence_low or "transit" in evidence_low:
            decision = "deny"
            rationale = "Orders cannot be cancelled once they have been shipped."
        else:
            decision = "approve"
            rationale = "Order is eligible for cancellation as it has not yet shipped."
    else:
        decision = "escalate"
        rationale = "Manual review required for this complex case."

    return {
        "classification": "refund" if "refund" in ticket_low else "other",
        "decision": decision,
        "rationale": rationale,
        "citations": citations,
        "customer_response": f"Based on our policy: {rationale}",
        "internal_notes": "Processed by SupportAI Pipeline."
    }
