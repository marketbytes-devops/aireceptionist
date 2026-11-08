# AyurVoice SaaS - System Architecture & Engineering Guide

## 1. Executive Summary
**AyurVoice SaaS** is a production-grade, multi-tenant AI voice receptionist platform engineered specifically for Ayurvedic clinics. The platform orchestrates inbound telephony (via Twilio), bidirectional real-time speech processing (via ElevenLabs Conversational AI), and dynamic scheduling databases (via PostgreSQL and FastAPI) to provide an autonomous receptionist experience.

---

## 2. High-Level System Architecture

```mermaid
flowchart TD
    subgraph Telephony & Caller Layer
        Caller([📞 Inbound Patient Call]) --> TwilioDID[Twilio Phone Number]
        TwilioDID -->|POST /api/v1/telephony/incoming-call| FastAPIGateway[FastAPI Telephony Gateway]
        FastAPIGateway -->|Returns TwiML <Connect><Stream>| TwilioDID
        TwilioDID <-->|WebSocket Audio Media Stream| WSSBridge[/api/v1/telephony/media-stream/{clinic_id}/]
    end

    subgraph ElevenLabs AI Layer
        WSSBridge <-->|Bi-directional Audio| ElevenLabsAgent[ElevenLabs Conversational AI Agent]
        ElevenLabsAgent -->|Tool: check-availability| ToolCheck[POST /api/v1/tools/check-availability]
        ElevenLabsAgent -->|Tool: book-appointment| ToolBook[POST /api/v1/tools/book-appointment]
        ElevenLabsAgent -->|Post-Call Webhook| WebhookPost[POST /api/v1/webhooks/elevenlabs-post-call]
    end

    subgraph Backend Core Services
        ToolCheck --> SlotEngine[Availability Slot Calculation Engine]
        ToolBook --> BookingEngine[Atomic Booking Service]
        WebhookPost --> CallLogEngine[Call Log & Transcript Processor]
        BookingEngine --> CeleryQueue[(Redis Broker)]
        CeleryQueue --> CeleryWorker[Celery Asynchronous Worker]
        CeleryWorker --> NotifDispatch[SMS / WhatsApp Dispatcher]
    end

    subgraph Multi-Tenant Database
        SlotEngine <--> PostgreSQL[(PostgreSQL Multi-Tenant DB)]
        BookingEngine <--> PostgreSQL
        CallLogEngine <--> PostgreSQL
    end

    subgraph Clinic Admin Portal
        AdminUser([Clinic Admin / Vaidya]) <--> NextDashboard[Next.js 15 / React 19 Portal]
        NextDashboard <-->|JWT Authenticated REST| FastAPIGateway
    end
```

---

## 3. Multi-Tenant Data Isolation Strategy

AyurVoice enforces tenant boundaries using **row-level `clinic_id` scoping**:
1. **Clinic Isolation**: Every business entity (`doctors`, `doctor_schedules`, `appointments`, `call_logs`, `users`) contains an indexed Foreign Key referencing `clinics.id`.
2. **JWT Claims & Role-Based Access Control**:
   - Access tokens issued to clinic admins encode `sub` (User ID), `role` (`clinic_admin`), and `clinic_id`.
   - The FastAPI dependency `get_current_clinic_admin` enforces that queries filter by `current_user.clinic_id`.
3. **Foreign Key Cascades**:
   - Clinic deletions cascade cleanly to child doctors, schedules, appointments, and call logs (`ondelete="CASCADE"`).
   - Deleting appointments safely retains call logs with `ondelete="SET NULL"` for audit and regulatory compliance.

---

## 4. Real-Time Voice & Tool Calling Lifecycle

```mermaid
sequenceDiagram
    autonumber
    actor Patient as Patient (Caller)
    participant Twilio as Twilio Voice API
    participant FastAPI as FastAPI Telephony
    participant ElevenLabs as ElevenLabs Agent
    participant DB as PostgreSQL DB
    participant Celery as Redis / Celery

    Patient->>Twilio: Dials Clinic Number (+1-800-555-0199)
    Twilio->>FastAPI: POST /api/v1/telephony/incoming-call
    FastAPI->>DB: Lookup Clinic by Phone Number
    DB-->>FastAPI: Clinic Record (Sree Kerala Ayurvedic)
    FastAPI-->>Twilio: TwiML <Connect><Stream url="wss://.../media-stream/{clinic_id}">
    Twilio<-->>ElevenLabs: Bidirectional Streaming Audio (G.711 mulaw)
    
    Note over Patient,ElevenLabs: Patient: "I'd like to book a Panchakarma session with Dr. Varma tomorrow"
    ElevenLabs->>FastAPI: POST /api/v1/tools/check-availability
    FastAPI->>DB: Query Doctor Schedules - Booked Appointments
    DB-->>FastAPI: Open Slots (10:00 AM, 11:30 AM, 02:00 PM)
    FastAPI-->>ElevenLabs: {"available": true, "message": "Dr. Varma is available at 10:00 AM..."}
    ElevenLabs-->>Patient: "Dr. Varma is available at 10:00 AM. Shall I confirm that for you?"
    
    Note over Patient,ElevenLabs: Patient: "Yes please, my name is Kavita Raman"
    ElevenLabs->>FastAPI: POST /api/v1/tools/book-appointment
    FastAPI->>DB: Insert Appointment (status: booked)
    FastAPI->>Celery: Queue confirmation SMS/WhatsApp task
    FastAPI-->>ElevenLabs: {"status": "success", "confirmation_id": "AYUR-8924"}
    ElevenLabs-->>Patient: "Your appointment is confirmed! Your booking ID is AYUR-8924."
    
    Note over Patient,Twilio: Call Disconnects
    ElevenLabs->>FastAPI: POST /api/v1/webhooks/elevenlabs-post-call (Duration, Audio URL, Full Transcript)
    FastAPI->>DB: Upsert CallLog & attach transcript to Appointment
```

---

## 5. Security & Secret Safeguards
- **Zero Secrets in Code**: All sensitive keys (`ELEVENLABS_API_KEY`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `SECRET_KEY`, `DATABASE_URL`) are read exclusively from environment variables using `pydantic-settings`.
- **Password Protection**: Passwords are encrypted using salted bcrypt hashing.
- **CORS Configuration**: Restricts API calls to approved origins while permitting tunneled webhook traffic.

