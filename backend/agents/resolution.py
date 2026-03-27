def resolution_agent(ticket_text, retrieved):
    # Use only retrieved chunks
    citations = [r["citation"] for r in retrieved]
    evidence = "\n".join([r["text"] for r in retrieved])
    # Simple logic: if no evidence, say not in policy
    if not evidence.strip():
        return {
            "classification": "other",
            "decision": "escalate",
            "rationale": "Not in policy.",
            "citations": [],
            "customer_response": "I don’t have that information in the policy.",
            "internal_notes": "Escalate to human."
        }
    # Example: always approve if 'refund' in evidence
    if "refund" in evidence.lower():
        decision = "approve"
        rationale = "Policy allows refund."
    else:
        decision = "deny"
        rationale = "Policy does not allow."    
    return {
        "classification": "refund" if "refund" in evidence.lower() else "other",
        "decision": decision,
        "rationale": rationale,
        "citations": citations,
        "customer_response": f"Decision: {decision}. See policy.",
        "internal_notes": ""
    }
