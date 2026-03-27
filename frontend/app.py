import streamlit as st
import requests
import json

API_URL = "http://localhost:8000"

st.set_page_config(page_title="SupportAI SaaS", layout="centered")
st.title("SupportAI SaaS Dashboard")

if "token" not in st.session_state:
    st.session_state.token = None

menu = st.sidebar.selectbox("Menu", ["Login", "Signup", "Dashboard", "Upload Policy", "Submit Ticket", "View Tickets", "View Responses"])

headers = {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

if menu == "Signup":
    st.subheader("Sign Up")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        r = requests.post(f"{API_URL}/auth/register", params={"name": name, "email": email, "password": password})
        st.success(r.json().get("msg", "Registered"))

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
    order_json = st.text_area("Order Context (JSON)", value='{"order_date": "", "delivery_date": "", "item_category": "", "order_status": "", "region": ""}')
    if st.button("Submit"):
        r = requests.post(f"{API_URL}/ticket/submit", params={"ticket_text": ticket_text, "order_json": order_json}, headers=headers)
        st.json(r.json())

elif menu == "View Tickets":
    st.subheader("Your Tickets")
    r = requests.get(f"{API_URL}/ticket/list", headers=headers)
    st.json(r.json())

elif menu == "View Responses":
    st.subheader("AI Responses")
    r = requests.get(f"{API_URL}/ticket/responses", headers=headers)
    st.json(r.json())
