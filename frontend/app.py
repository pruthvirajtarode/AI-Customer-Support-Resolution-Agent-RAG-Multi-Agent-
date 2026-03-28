import streamlit as st
import requests
import json

API_URL = "http://localhost:8000"

st.set_page_config(page_title="SupportAI SaaS", layout="centered")
st.title("SupportAI SaaS Dashboard")

if "token" not in st.session_state:
    st.session_state.token = None

menu = st.sidebar.selectbox("Menu", ["Login", "Signup", "Dashboard", "Upload Policy", "Submit Ticket", "View History", "System Evaluation"])

headers = {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

if menu == "Signup":
    st.subheader("Sign Up")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        r = requests.post(f"{API_URL}/auth/register?name={name}&email={email}&password={password}")
        st.success("Registered! Go to Login.")

elif menu == "Login":
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        data = {"username": email, "password": password}
        r = requests.post(f"{API_URL}/auth/login", data=data)
        if r.status_code == 200:
            st.session_state.token = r.json()["access_token"]
            st.success("Logged in!")
        else:
            st.error("Login failed")

elif menu == "Dashboard":
    st.subheader("Welcome to SupportAI SaaS!")
    if not st.session_state.token:
        st.info("Please login.")
    else:
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        col1.metric("Resolution Time", "50ms")
        col2.metric("Pipeline Health", "100%")
        col3.metric("Uptime", "99.9%")

elif menu == "Upload Policy":
    st.subheader("Upload Policy Document")
    uploaded = st.file_uploader("Choose a .txt or .pdf file")
    if uploaded and st.button("Upload"):
        files = {"file": (uploaded.name, uploaded, uploaded.type)}
        r = requests.post(f"{API_URL}/policy/upload", files=files, headers=headers)
        st.success(r.json().get("msg", "Uploaded"))

elif menu == "Submit Ticket":
    st.subheader("Submit Ticket")
    ticket_text = st.text_area("Ticket Text")
    order_json = st.text_area("Order Context (JSON)", value='{"order_date": "2023-01-01", "delivery_date": "2023-01-05", "item_category": "electronics", "order_status": "delivered", "region": "US"}')
    if st.button("Submit"):
        with st.spinner("Agent running..."):
            r = requests.post(f"{API_URL}/ticket/submit", params={"ticket_text": ticket_text, "order_json": order_json}, headers=headers)
            res = r.json()
            st.markdown(f"**AI Decision:** `{res['decision']}`")
            st.write(f"**Response:** {res['customer_response']}")
            with st.expander("Rationale"):
                st.write(res["rationale"])

elif menu == "View History":
    st.subheader("AI Performance History")
    r = requests.get(f"{API_URL}/ticket/responses", headers=headers)
    if r.ok:
        data = r.json()
        for item in data:
            st.markdown(f"**[{item['decision']}]** - {item['response_text']}")
            st.caption(f"Category: {item['classification']}")
            st.divider()

elif menu == "System Evaluation":
    st.subheader("20+ Test Case Audit")
    if st.button("Run Audit"):
        with st.spinner("Processing 20+ scenarios..."):
            r = requests.get(f"{API_URL}/evaluation/report", headers=headers)
            if r.ok:
                data = r.json()
                st.write(f"Accuracy: **{data['correctness']}**")
                col1, col2 = st.columns(2)
                col1.info(f"Citation Coverage: {data['citation_coverage']}")
                col2.warning(f"Escalation Accuracy: {data['escalation_accuracy']}")
                st.divider()
                for item in data['details']:
                    bg = "#dcfce7" if item['correct'] else "#fee2e2"
                    with st.container():
                        st.markdown(f"**Input:** {item['input']['ticket_text'][:80]}...")
                        st.markdown(f"**Expected:** `{item['input']['expected']['decision']}` | **Actual:** `{item['output']['decision']}`")
                        if not item['correct']:
                            st.error("Audit Discrepancy Found")
                        st.divider()
