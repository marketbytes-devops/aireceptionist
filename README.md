# AyurVoice SaaS 🌿
### Autonomous Multi-Tenant AI Voice Receptionist Platform for Ayurvedic Clinics

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js 15](https://img.shields.io/badge/Frontend-Next.js%2015-000000.svg?style=flat&logo=next.js)](https://nextjs.org)
[![ElevenLabs](https://img.shields.io/badge/Voice%20AI-ElevenLabs%20Conversational%20AI-black.svg?style=flat)](https://elevenlabs.io)
[![Twilio](https://img.shields.io/badge/Telephony-Twilio%20Voice-F22F46.svg?style=flat&logo=twilio)](https://twilio.com)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791.svg?style=flat&logo=postgresql)](https://postgresql.org)
[![Celery](https://img.shields.io/badge/Queue-Celery%20%2B%20Redis-37814A.svg?style=flat&logo=celery)](https://docs.celeryq.dev)

AyurVoice SaaS is a complete, production-ready multi-tenant AI voice receptionist platform designed for Ayurvedic hospitals and clinics. It allows clinic owners to onboard their clinics, configure doctor timetables, manage treatments (Panchakarma, Nadi Pariksha, Dietetics), inspect real-time patient bookings, and autonomously answer inbound patient calls using **ElevenLabs Conversational AI** and **Twilio**.

---

## 🌟 Key Features

1. **Multi-Tenant Architecture**: Complete data isolation via row-level `clinic_id` constraints and JWT authentication.
2. **Autonomous Voice Receptionist**: Handles patient calls, understands Ayurvedic specialties, checks doctor availability dynamically, and reserves appointments.
3. **ElevenLabs Tool Calling Webhooks**:
   - `POST /api/v1/tools/check-availability`: Real-time calendar calculation against doctor schedules and booked appointments.
   - `POST /api/v1/tools/book-appointment`: Atomic double-booking prevention, booking confirmation code generation, and SMS/WhatsApp dispatch.
4. **Twilio Telephony & Media Stream Bridge**:
   - Inbound webhook generates TwiML (`<Connect><Stream>`) to bridge bidirectional audio to ElevenLabs WebSocket.
5. **Post-Call Analytics & NLP**:
   - Automatic recording indexing, caller sentiment analysis, summary extraction, and transcript storage.
6. **Modern Clinic Admin Dashboard**:
   - Built with Next.js 15, React 19, Tailwind CSS, and Lucide Icons.
   - Interactive Doctor Timings Manager, Appointments Table, Call Audio Player, and in-browser AI Voice Simulator.

---

## 📁 Project Directory Structure

```text
ayurvoice/
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── api/v1/           # REST endpoints & webhooks (auth, clinics, doctors, tools, telephony)
│   │   ├── core/             # Database session, config, security & auth dependencies
│   │   ├── models/           # SQLAlchemy ORM models (Base, Clinic, Doctor, Schedule, Appointment, CallLog, User)
│   │   ├── schemas/          # Pydantic validation schemas
│   │   ├── services/         # Availability engine, Booking service, Telephony bridge, Notifications
│   │   ├── tasks/            # Celery tasks & Redis worker
│   │   └── main.py           # FastAPI entrypoint, lifespan seeding, CORS
│   ├── alembic/              # Database migration configurations & versions
│   ├── tests/                # Automated pytest suite (7 passing integration tests)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/                 # Next.js 15 / React 19 Admin Dashboard
│   ├── src/
│   │   ├── app/              # Next.js App Router (overview, appointments, doctors, calls, simulator)
│   │   ├── components/       # UI Components (Sidebar, Header, StatCard, TranscriptModal)
│   │   └── lib/              # Types & API client
│   ├── package.json
│   ├── tailwind.config.js
│   ├── Dockerfile
│   └── .env.example
├── docs/                     # Comprehensive Architecture & Setup Guides
│   ├── ARCHITECTURE.md       # High-level architecture, diagrams, tenant security
│   ├── API_REFERENCE.md      # Complete REST API reference with payloads
│   ├── ELEVENLABS_TWILIO_SETUP.md # Step-by-step ElevenLabs agent & Twilio setup
│   └── DATABASE_SCHEMA.md    # ER diagram & database definitions
├── docker-compose.yml        # PostgreSQL, Redis, Backend, Celery, and Frontend orchestration
└── README.md
```

---

## 🚀 Quick Start Guide

### Option 1: Docker Compose (All-in-One)
```bash
# Clone the repository and run:
docker-compose up --build
```
- **Admin Dashboard**: `http://localhost:3000`
- **FastAPI Backend & Swagger**: `http://localhost:8000/docs`

---

### Option 2: Local Development Setup

#### 1. Backend Setup (FastAPI)
```bash
cd backend

# Create virtual environment and activate
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic -c alembic.ini upgrade head

# Start FastAPI development server
uvicorn app.main:app --reload --port 8000
```
- Interactive Swagger UI: `http://localhost:8000/docs`

#### 2. Frontend Setup (Next.js)
```bash
cd frontend

# Install npm dependencies
npm install

# Start Next.js development server
npm run dev
```
- Access dashboard: `http://localhost:3000`

---

## 🧪 Running Automated Tests

Run the backend integration test suite:
```bash
cd backend
pytest -c pytest.ini tests -v
```

All 7 test suites verify:
- Clinic onboarding and doctor scheduling
- Doctor availability calculation engine
- ElevenLabs `check-availability` tool execution
- ElevenLabs `book-appointment` tool execution and conflict prevention
- Twilio incoming call TwiML generation
- ElevenLabs post-call transcript and analytics webhook
- JWT authentication and dashboard analytics

---

## 📞 ElevenLabs & Twilio Telephony Setup

Refer to [`docs/ELEVENLABS_TWILIO_SETUP.md`](docs/ELEVENLABS_TWILIO_SETUP.md) for complete instructions on:
1. Exposing local server with ngrok: `ngrok http 8000`.
2. Setting Twilio Voice incoming call webhook to `https://<ngrok-id>.ngrok-free.app/api/v1/telephony/incoming-call`.
3. Adding custom tools `check_availability` and `book_appointment` in your ElevenLabs Conversational AI dashboard.

---

## 🛡️ License & Credits
Engineered for modern Ayurvedic clinics and wellness centers. Released under the MIT License.

