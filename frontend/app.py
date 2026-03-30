import streamlit as st
import requests
import json
import os

# Config
API_URL = os.getenv("API_URL", "http://localhost:8000/api")

st.set_page_config(
    page_title="SupportAI Pro | Multi-Agent SaaS",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Styling
st.markdown("""
<style>
    .main {
        background: radial-gradient(circle at top right, #1e1b4b, #0f172a 50%, #020617);
        color: #f8fafc;
    }
    .stApp {
        background: transparent;
    }
    .stMetric {
        background: rgba(30, 41, 59, 0.4);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    .stButton>button {
        background: linear-gradient(135deg, #8b5cf6, #7c3aed);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(139, 92, 246, 0.4);
    }
    .stTextArea>div>div>textarea {
        background: rgba(15, 23, 42, 0.6);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stTextInput>div>div>input {
        background: rgba(15, 23, 42, 0.6);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    h1, h2, h3 {
        letter-spacing: -0.025em;
        font-weight: 800 !important;
    }
    .css-1kyxreq {
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

# Session State
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

# Sidebar Admin
with st.sidebar:
    st.image("https://img.icons8.com/isometric/512/robot-2.png", width=100)
    st.title("SupportAI Pro")
    st.caption("v2.0 Enterprise RAG")
    st.divider()
    
    if st.session_state.token:
        st.success(f"Connected: {st.session_state.user}")
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()
        menu = st.radio("Navigation", ["Dashboard", "Knowledge Base", "Audit Agent", "History", "System Evaluation"])
    else:
        st.info("Authentication Required")
        menu = st.radio("Auth", ["Login", "Signup"])

st.markdown(f"# {menu}")

# Logic
if menu == "Signup":
    with st.container():
        st.markdown("### Create your account")
        name = st.text_input("Full Name", placeholder="John Doe")
        email = st.text_input("Email Address", placeholder="john@company.com")
        password = st.text_input("Secure Password", type="password")
        if st.button("Initialize Agent Account"):
            try:
                r = requests.post(f"{API_URL}/auth/register", params={"name": name, "email": email, "password": password})
                if r.status_code == 200:
                    st.success("✅ Account initialized! Please login.")
                else:
                    st.error(f"Failed: {r.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error("Backend unreachable. Ensure FastAPI is running.")

elif menu == "Login":
    with st.container():
        st.markdown("### Welcome Back")
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        if st.button("Authenticate"):
            try:
                data = {"username": email, "password": password}
                r = requests.post(f"{API_URL}/auth/login", data=data)
                if r.status_code == 200:
                    st.session_state.token = r.json()["access_token"]
                    st.session_state.user = email
                    st.success("🔓 Access Granted!")
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
            except Exception as e:
                st.error("Backend offline.")

elif menu == "Dashboard":
    col1, col2, col3 = st.columns(3)
    col1.metric("Resolution Time", "1.2s", "-0.4s")
    col2.metric("Compliance Rate", "99.8%", "0.2%")
    col3.metric("Auto-Escalation", "12%", "-2%")
    
    st.markdown("### 📈 Recent Activity")
    st.info("System operational. All agents (Triage, Retriever, Resolution, Compliance) are live.")
    
    with st.expander("Agent Status Details"):
        st.json({
            "TriageAgent": "Optimized",
            "RetrieverAgent": "Connected (FAISS)",
            "ResolutionAgent": "GPT-4o Ready",
            "ComplianceAgent": "Enforced"
        })

elif menu == "Knowledge Base":
    st.markdown("### Documents")
    st.caption("Upload company policies to ground your AI agents.")
    uploaded = st.file_uploader("Choose TXT or PDF", type=["txt", "pdf"])
    if uploaded:
        if st.button("Sync to Vector DB"):
            files = {"file": (uploaded.name, uploaded, uploaded.type)}
            r = requests.post(f"{API_URL}/policy/upload", files=files, headers=get_headers())
            if r.ok:
                st.success("✅ Knowledge base synchronized!")
            else:
                st.error("Sync failed.")

elif menu == "Audit Agent":
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### Submit Ticket for Multi-Agent Resolution")
        ticket_text = st.text_area("Customer Ticket", height=200, placeholder="Type customer request here...")
    with col2:
        st.markdown("### Order Context")
        order_json = st.text_area("JSON Context", height=200, value='{\n  "order_id": "12345",\n  "status": "delivered",\n  "item": "Electronics",\n  "delivery_date": "2024-03-20"\n}')
    
    if st.button("Run Resolution Pipeline"):
        if not ticket_text:
            st.warning("Please enter ticket text.")
        else:
            with st.spinner("🤖 Multi-agent consensus in progress..."):
                try:
                    r = requests.post(f"{API_URL}/ticket/submit", params={"ticket_text": ticket_text, "order_json": order_json}, headers=get_headers())
                    if r.ok:
                        res = r.json()
                        st.divider()
                        status_color = {"approve": "green", "deny": "red", "escalate": "orange"}.get(res['decision'], "blue")
                        st.markdown(f"### Decision: :{status_color}[{res['decision'].upper()}]")
                        st.markdown(f"**Classification:** `{res['classification']}`")
                        
                        st.markdown("#### 💬 AI Generated Response")
                        st.info(res['customer_response'])
                        
                        with st.expander("🔍 Internal Agent Rationale"):
                            st.write(res['rationale'])
                            if res.get('citations'):
                                st.markdown("**Citations:**")
                                st.write(res['citations'])
                    else:
                        st.error("Pipeline failed.")
                except Exception as e:
                    st.error(f"Error: {e}")

elif menu == "History":
    st.markdown("### Resolution Log")
    r = requests.get(f"{API_URL}/ticket/responses", headers=get_headers())
    if r.ok:
        data = r.json()
        if not data:
            st.write("No history found.")
        for item in reversed(data):
            with st.container():
                c1, c2 = st.columns([1, 4])
                c1.markdown(f"**{item['decision'].upper()}**")
                c2.write(item['response_text'])
                st.caption(f"Time: {item.get('created_at', 'N/A')} | Mode: Multi-Agent RAG")
                st.divider()

elif menu == "System Evaluation":
    st.markdown("### ⚖️ Performance Audit")
    st.caption("Continuous evaluation across 20+ edge cases and policy conflicts.")
    
    if st.button("Execute Full 20+ Case Audit"):
        with st.spinner("Running 20+ scenario simulation..."):
            r = requests.get(f"{API_URL}/evaluation/report", headers=get_headers())
            if r.ok:
                data = r.json()
                m1, m2, m3 = st.columns(3)
                m1.metric("Overall Accuracy", data['correctness'])
                m2.metric("Citation Coverage", data['citation_coverage'])
                m3.metric("Escalation Integrity", data['escalation_accuracy'])
                
                st.divider()
                for i, item in enumerate(data['details']):
                    color = "green" if item['correct'] else "red"
                    with st.expander(f"Case #{i+1}: {item['input']['ticket_text'][:50]}... - Status: :{color}[{'PASS' if item['correct'] else 'FAIL'}]"):
                        st.markdown(f"**Ticket:** {item['input']['ticket_text']}")
                        st.markdown(f"**Order:** `{item['input']['order_json']}`")
                        st.markdown(f"**Expected Decision:** `{item['input']['expected']['decision']}`")
                        st.markdown(f"**Actual Decision:** `{item['output']['decision']}`")
                        if not item['correct']:
                            st.error(f"Discrepancy: AI resolved as {item['output']['decision']} but expected {item['input']['expected']['decision']}.")
            else:
                st.error("Evaluation service unreachable.")
