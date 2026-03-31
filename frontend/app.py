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
                # Backend expects /api/auth/signup with JSON body
                r = requests.post(f"{API_URL}/auth/signup", json={"email": email, "password": password, "full_name": name})
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
                # OAuth2 expects 'username' and 'password' as form data
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
    try:
        r = requests.get(f"{API_URL}/ticket/stats", headers=get_headers())
        if r.ok:
            data = r.json()
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Audits", data['total_audits'])
            col2.metric("Compliance Rate", data['compliance_rate'])
            col3.metric("Avg Latency", data['avg_latency'])
            
            st.markdown("### 📈 Recent Activity")
            # Render chart from activity data
            if 'activity' in data:
                import pandas as pd
                df = pd.DataFrame(data['activity'])
                st.bar_chart(df.set_index('day'))
        else:
            st.warning("Could not sync dashboard metrics.")
    except Exception:
        st.error("Stats service error.")

elif menu == "Knowledge Base":
    st.markdown("### Documents")
    st.caption("Upload company policies to ground your AI agents.")
    uploaded = st.file_uploader("Choose TXT or PDF", type=["txt", "pdf"])
    if uploaded:
        if st.button("Sync to Vector DB"):
            files = {"file": (uploaded.name, uploaded, uploaded.type)}
            # Backend expects /api/policy/sync
            r = requests.post(f"{API_URL}/policy/sync", files=files, headers=get_headers())
            if r.ok:
                res = r.json()
                st.success(f"✅ Knowledge base synchronized! Index: {res.get('indexed_chunks', 0)} nodes.")
            else:
                st.error("Sync failed.")

elif menu == "Audit Agent":
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### Submit Ticket for Multi-Agent Resolution")
        ticket_text = st.text_area("Customer Ticket", height=200, placeholder="Type customer request here...")
    with col2:
        st.markdown("### Order Context")
        order_json_input = st.text_area("JSON Context", height=200, value='{\n  "order_id": "ORD-12345",\n  "status": "delivered",\n  "category": "electronics"\n}')
    
    if st.button("Run Resolution Pipeline"):
        if not ticket_text:
            st.warning("Please enter ticket text.")
        else:
            try:
                order_json = json.loads(order_json_input)
            except json.JSONDecodeError:
                st.error("Invalid JSON in Order Context")
                st.stop()

            with st.spinner("🤖 Multi-agent consensus in progress..."):
                try:
                    # Backend expects /api/ticket/audit with JSON body
                    r = requests.post(f"{API_URL}/ticket/audit", json={"text": ticket_text, "order_json": order_json}, headers=get_headers())
                    if r.ok:
                        res = r.json()
                        st.divider()
                        decision = res['resolution']['decision']
                        status_color = {"approve": "green", "deny": "red", "escalate": "orange"}.get(decision.lower(), "blue")
                        st.markdown(f"### Decision: :{status_color}[{decision.upper()}]")
                        st.markdown(f"**Classification:** `{res['triage_result']['category']}`")
                        
                        st.markdown("#### 💬 AI Generated Response")
                        st.info(res['resolution']['explanation'])
                        
                        with st.expander("🔍 Internal Agent Rationale"):
                            st.write(res.get('rationale', 'Rationale in explanation.'))
                            if res.get('citations'):
                                st.markdown("**Citations:**")
                                st.write(res['citations'])
                    else:
                        st.error(f"Pipeline failed: {r.status_code}")
                except Exception as e:
                    st.error(f"Error: {e}")

elif menu == "History":
    st.markdown("### Resolution Log")
    r = requests.get(f"{API_URL}/ticket/history", headers=get_headers())
    if r.ok:
        data = r.json()
        if not data:
            st.write("No history found.")
        for item in data:
            with st.container():
                c1, c2 = st.columns([1, 4])
                decision = item['decision']
                status_color = ":green" if decision.lower() == "approve" else ":red" if decision.lower() == "deny" else ":orange"
                c1.markdown(f"**{status_color}[{decision.upper()}]**")
                c2.write(item['response_text'])
                st.caption(f"Category: {item['category']} | Mode: Multi-Agent RAG")
                st.divider()
    else:
        st.error("History sync error.")

elif menu == "System Evaluation":
    st.markdown("### ⚖️ Performance Audit")
    st.caption("Continuous evaluation across 20+ edge cases and policy conflicts.")
    
    if st.button("Execute Full 20+ Case Audit"):
        with st.spinner("Running 20+ scenario simulation..."):
            # Backend expects /api/evaluation/run
            r = requests.post(f"{API_URL}/evaluation/run", headers=get_headers())
            if r.ok:
                data = r.json()
                m1, m2 = st.columns(2)
                m1.metric("Overall Accuracy", f"{data['summary']['correctness_rate'] * 100:.1f}%")
                m2.metric("Total Cases", data['summary']['total_cases'])
                
                st.divider()
                for i, item in enumerate(data['results']):
                    color = "green" if item['is_correct'] else "red"
                    with st.expander(f"Case #{item['case_id']}: {item['ticket_text'][:50]}... - Status: :{color}[{'PASS' if item['is_correct'] else 'FAIL'}]"):
                        st.markdown(f"**Ticket:** {item['ticket_text']}")
                        st.markdown(f"**Result Decision:** `{item['result']['decision']}`")
                        st.markdown(f"**Expected Decision:** `{item['expected']['decision']}`")
                        if not item['is_correct']:
                            st.error(f"Discrepancy: AI resolved as {item['result']['decision']} but expected {item['expected']['decision']}.")
            else:
                st.error("Evaluation service unreachable.")
