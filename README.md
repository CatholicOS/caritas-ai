# Welcome to CaritasAI


**CaritasAI** is an open-source Agentic AI platform that helps Catholic parishes, charities, and volunteers connect in real-time.  
Using Large Language Models (LLMs), geospatial data, and automation, CaritasAI transforms “I want to help” into immediate local action.

---

## ✝️ Mission
CaritasAI supports the Church’s mission of mercy and service by building a digital bridge between **those who want to help** and **those who need help**.  

It enables parishes, dioceses, and volunteers to coordinate charitable activities efficiently using an AI-powered conversational interface.

---

## Features
- 🤖 **AI Volunteer Agent** – Conversational assistant.
- 🌍 **Geospatial Search** – Finds nearby parishes, charities, and service opportunities.
- 📅 **Smart Scheduling** – Suggests events and registers volunteers automatically. 
- 💬 **Multichannel Integration** – Chat via Web, SMS (Twilio), or WhatsApp  
- 🔒 **Secure, Privacy-first Design** – Minimal PII, opt-in data, localizable architecture  

---

## 🧠 System Architecture
CaritasAI uses a modular, service-oriented architecture:

🖼️ See: [`docs/architecture_diagram.png`](docs/architecture_diagram.png)  
📘 Full design: [`docs/system_design.md`](docs/system_design.md)

---

## 🧰 Tech Stack

| Layer | Technologies |
|--------|---------------|
| **Frontend** | React |
| **Backend API** | FastAPI |
| **AI / Reasoning** | LangChain, OpenAI GPT-4  |
| **Database** | PostgreSQL + PostGIS |
| **Integrations** | Twilio (SMS), Google Maps API, Airtable |
| **Deployment** | Docker, AWS EC2  |

---


## ⚙️ Local Development Setup

### 🧩 Prerequisites
- Python 3.11+
- PostgreSQL (local or via Docker)
- VS Code (recommended)
- Optional: OpenAI API key
---
 
### Clone the Repository
```bash
git clone https://github.com/CatholicOS/caritas-ai.git

cd caritas-ai
```
---

###  Dev Quickstart
```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

🐳 Run with Docker
```
docker compose up --build
```
API → http://localhost:8000
Adminer (DB UI) → http://localhost:8080

---

## 🙏 Acknowledgements
CaritasAI is being developed as part of the **All Saints Hackathon 2025**, organized by [Catholic Open Source (CatholicOS)](https://github.com/CatholicOS).  
Special thanks to the organizers, mentors, and the Catholic developer community inspiring innovation through faith and technology.

---
## 💡 Get Involved
We welcome contributions.
Please follow PEP 8 these standards to ensure code quality, clarity, and maintainability across the CaritasAI ecosystem.







