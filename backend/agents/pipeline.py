from backend.agents.triage import triage_agent
from backend.agents.retriever import retriever_agent
from backend.agents.resolution import resolution_agent
from backend.agents.compliance import compliance_agent
from backend.rag.pipeline import load_user_faiss

def process_ticket(ticket, user_id):
    # 1. Triage
    triage = triage_agent(ticket.ticket_text)
    # 2. Retrieve
    vectordb = load_user_faiss(user_id)
    if vectordb is None:
        return {
            "classification": "other",
            "decision": "escalate",
            "rationale": "No policy index found.",
            "citations": [],
            "customer_response": "I don't have access to policy documents yet. Please upload a policy PDF.",
            "internal_notes": "Policy missing."
        }
    retrieved = retriever_agent(ticket.ticket_text, vectordb)
    # 3. Resolution
    resolution = resolution_agent(ticket.ticket_text, retrieved, ticket.order_json, initial_triage=triage)
    # 4. Compliance
    compliance = compliance_agent(resolution, retrieved)
    if not compliance["valid"]:
        resolution["decision"] = "escalate"
        resolution["customer_response"] = "Escalated to human agent."
    return {
        "triage_result": triage,
        "resolution": resolution,
        "classification": triage["category"],
        "decision": resolution["decision"]
    }
