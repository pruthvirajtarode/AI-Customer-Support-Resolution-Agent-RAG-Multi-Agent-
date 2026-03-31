from backend.agents.triage import triage_agent
from backend.agents.retriever import retriever_agent
from backend.agents.resolution import resolution_agent
from backend.agents.compliance import compliance_agent
from backend.rag.pipeline import load_user_faiss

def process_ticket(ticket, user_id, db=None):
    # 1. Triage
    triage = triage_agent(ticket.ticket_text)
    
    # 2. Retrieve (with fallback recovery from DB)
    vectordb = load_user_faiss(user_id, db=db)
    
    if vectordb is None:
        return {
            "classification": triage.get("category", "other"),
            "decision": "escalate",
            "rationale": "No policy documents found in knowledge base.",
            "customer_response": "I'm sorry, I don't have access to the company policy dashboard at the moment. Please upload a policy document.",
            "citations": []
        }
        
    retrieved = retriever_agent(ticket.ticket_text, vectordb)
    
    # 3. Resolution
    resolution = resolution_agent(ticket.ticket_text, retrieved, ticket.order_json, initial_triage=triage)
    
    # 4. Compliance
    compliance = compliance_agent(resolution, retrieved)
    if not compliance["valid"]:
        resolution["decision"] = "escalate"
        resolution["customer_response"] = "Escalated for manual compliance review."
    
    return {
        "classification": triage.get("category", "other"),
        "decision": resolution.get("decision", "escalate"),
        "rationale": resolution.get("rationale", ""),
        "customer_response": resolution.get("customer_response", ""),
        "citations": resolution.get("citations", []),
        # Support for app.js nested structure
        "triage_result": {"category": triage.get("category", "other")},
        "resolution": {
            "decision": resolution.get("decision", "escalate"),
            "explanation": resolution.get("customer_response", "") or resolution.get("explanation", "")
        }
    }
