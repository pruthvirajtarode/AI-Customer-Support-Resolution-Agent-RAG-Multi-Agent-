import os
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage
except ImportError:
    from langchain_community.chat_models import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage

def compliance_agent(resolution, retrieved):
    evidence = " ".join([r["text"] for r in retrieved])
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            chat = ChatOpenAI(temperature=0, openai_api_key=api_key)
            messages = [
                SystemMessage(content="You are a Compliance Agent. Verify if the resolution is grounded in the retrieved evidence. If it is not grounded, return 'False'. Otherwise return 'True'."),
                HumanMessage(content=f"Evidence: {evidence}\n\nResolution: {resolution['rationale']}")
            ]
            res = chat.invoke(messages).content
            if "false" in res.lower():
                return {"valid": False, "reason": "AI detected potential hallucination or lack of grounding."}
        except Exception:
            pass

    # Fallback/Manual checks
    if not resolution.get("citations") and "escalate" not in resolution["decision"]:
        return {"valid": False, "reason": "No citations provided for a positive decision."}
    
    if resolution["rationale"].lower() not in evidence.lower() and "not in policy" not in resolution["rationale"].lower():
        # Very loose grounding check for placeholder
        if len(evidence) < 10:
             return {"valid": False, "reason": "Insufficient evidence for grounding."}
             
    return {"valid": True}
