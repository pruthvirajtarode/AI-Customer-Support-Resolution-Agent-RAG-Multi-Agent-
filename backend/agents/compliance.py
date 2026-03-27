def compliance_agent(resolution, retrieved):
    # Check citations exist
    if not resolution.get("citations"):
        return {"valid": False, "reason": "No citations"}
    # Check claims are grounded
    evidence = " ".join([r["text"] for r in retrieved])
    if resolution["rationale"].lower() not in evidence.lower() and "not in policy" not in resolution["rationale"].lower():
        return {"valid": False, "reason": "Rationale not grounded"}
    return {"valid": True}
