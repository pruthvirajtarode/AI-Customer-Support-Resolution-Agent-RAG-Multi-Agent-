
<div align="center">
	<h1>🤖 SupportAI SaaS</h1>
	<p><b>AI-Powered Customer Support Resolution System (RAG + Multi-Agent)</b></p>
	<p>
		<img src="https://img.shields.io/badge/Backend-FastAPI-blue" />
		<img src="https://img.shields.io/badge/Frontend-Streamlit-green" />
		<img src="https://img.shields.io/badge/Database-PostgreSQL-blueviolet" />
		<img src="https://img.shields.io/badge/AI-LangChain%20%2B%20FAISS-orange" />
		<img src="https://img.shields.io/badge/Auth-JWT%20%2B%20bcrypt-yellow" />
		<img src="https://img.shields.io/badge/License-MIT-lightgrey" />
	</p>
</div>

---

## 🚀 Overview

<b>SupportAI SaaS</b> is a production-ready, multi-tenant SaaS platform for AI-powered customer support ticket resolution. It leverages a multi-agent RAG (Retrieval-Augmented Generation) architecture to ensure safe, accurate, and policy-grounded responses for every support ticket.

---

## 🏗️ Features

- 🔒 **User Authentication** (JWT, bcrypt, multi-user isolation)
- 📄 **Policy Document Upload** (txt/pdf, chunking, embedding, FAISS vector DB)
- 🤖 **Multi-Agent AI Pipeline** (Triage, Retriever, Resolution, Compliance)
- 🎫 **Ticket Submission & AI Response** (with citations, no hallucination)
- 📊 **Evaluation Module** (20+ test cases, auto-report)
- 🖥️ **Dashboard** (Streamlit UI: login, upload, submit, view results)
- 🗄️ **PostgreSQL + SQLAlchemy ORM**
- 🧠 **LangChain + FAISS + OpenAI/HuggingFace Embeddings**

---

## 📂 Project Structure

```
backend/
	main.py
	database/
	models/
	routes/
	agents/
	rag/
frontend/
requirements.txt
README.md
```

---

## ⚡ Quickstart

### 1. Backend Setup

```bash
cd backend
cp .env.example .env  # Edit with your DB and OpenAI keys
pip install -r ../requirements.txt
uvicorn main:app --reload
```

### 2. Frontend Setup (Streamlit)

```bash
cd ..
streamlit run frontend/app.py
```

---

## 🔑 API Endpoints

| Endpoint              | Method | Description                  |
|-----------------------|--------|------------------------------|
| /auth/register        | POST   | Register new user            |
| /auth/login           | POST   | Login, get JWT token         |
| /policy/upload        | POST   | Upload policy document       |
| /ticket/submit        | POST   | Submit support ticket        |
| /ticket/list          | GET    | List user tickets            |
| /ticket/responses     | GET    | List AI responses            |
| /evaluation/report    | GET    | Run evaluation & get report  |

---

## 🛡️ Safety & Compliance

- ❌ No hallucination: All answers are grounded in uploaded policy documents
- 📑 Citations required for every AI response
- 🚨 If not in policy, escalate to human or respond: "I don’t have that information in the policy."
- 🔍 Compliance agent validates every output

---

## 🧪 Evaluation Module

- 20+ test cases (normal, exception, conflict, not-in-policy)
- Metrics: citation coverage, correctness, escalation accuracy
- Auto-generated evaluation report via `/evaluation/report`

---

## 📸 Screenshots

<details>
<summary>Click to expand</summary>

**Login / Signup**

![Login](https://user-images.githubusercontent.com/your-username/login.png)

**Dashboard**

![Dashboard](https://user-images.githubusercontent.com/your-username/dashboard.png)

**Upload Policy**

![Upload](https://user-images.githubusercontent.com/your-username/upload.png)

**Submit Ticket**

![Ticket](https://user-images.githubusercontent.com/your-username/ticket.png)

**AI Response**

![Response](https://user-images.githubusercontent.com/your-username/response.png)

</details>

---

## 👨‍💻 Authors & Credits

- [Pruthviraj Tarode](https://github.com/pruthvirajtarode)
- Powered by FastAPI, Streamlit, LangChain, FAISS, OpenAI/HuggingFace

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
