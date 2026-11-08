# AyurVoice SaaS - API Reference

Base API Path: `/api/v1`

---

## 1. Authentication Endpoints

### Login (JSON)
- **Endpoint:** `POST /api/v1/auth/login`
- **Request Body:**
  ```json
  {
    "email": "admin@ayurvoice.com",
    "password": "AyurVoice2026!"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user_id": "9b14a705-...",
    "clinic_id": "c1111111-...",
    "role": "clinic_admin",
    "full_name": "Dr. Rajesh Varma",
    "email": "admin@ayurvoice.com"
  }
  ```

### Current User Profile
- **Endpoint:** `GET /api/v1/auth/me`
- **Headers:** `Authorization: Bearer <access_token>`
- **Response (200 OK):** User entity details.

---

## 2. Clinic Management

### Register New Clinic
- **Endpoint:** `POST /api/v1/clinics`
- **Request Body:**
  ```json
  {
    "name": "Kottakkal Arya Vaidya Sala Branch",
    "slug": "kottakkal-branch-1",
    "phone_number": "+18005550199",
    "address": "Malappuram, Kerala",
    "timezone": "Asia/Kolkata",
    "admin_name": "Chief Vaidya",
    "admin_email": "vaidya@kottakkal.example",
    "admin_password": "SecurePassword123!"
  }
  ```
- **Response (201 Created):** Clinic details.

### Get Clinic Doctors & Schedules
- **Endpoint:** `GET /api/v1/clinics/{clinic_id}/schedule`
- **Response (200 OK):** List of doctors with their active weekly schedule matrices.

---

## 3. ElevenLabs Conversational AI Tools (Webhooks)

### Check Doctor Availability
Called dynamically by ElevenLabs Agent during an active phone conversation.
- **Endpoint:** `POST /api/v1/tools/check-availability`
- **Request Body:**
  ```json
  {
    "clinic_id": "c1111111-2222-3333-4444-555555555555",
    "doctor_name": "Dr. Varma",
    "date_time": "2026-11-10T10:00:00",
    "treatment_type": "Panchakarma Consultation"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "available": true,
    "message": "Yes, Dr. Rajesh Varma is available on Tuesday, November 10 at 10:00 AM. Would you like me to book this appointment for you?",
    "available_slots": ["2026-11-10T10:00:00+00:00"],
    "doctor_id": "d1111111-...",
    "doctor_name": "Dr. Rajesh Varma",
    "consultation_fee": 600.0
  }
  ```

### Book Appointment
Called dynamically by ElevenLabs Agent once the patient confirms their booking details.
- **Endpoint:** `POST /api/v1/tools/book-appointment`
- **Request Body:**
  ```json
  {
    "clinic_id": "c1111111-2222-3333-4444-555555555555",
    "doctor_name": "Dr. Varma",
    "patient_name": "Kavita Raman",
    "patient_phone": "+919876543210",
    "patient_email": "kavita@example.com",
    "appointment_time": "2026-11-10T10:00:00",
    "treatment_type": "Panchakarma Consultation",
    "notes": "Patient reports chronic neck pain."
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "status": "success",
    "confirmation_id": "AYUR-7291",
    "appointment_id": "a1111111-...",
    "doctor_name": "Dr. Rajesh Varma",
    "appointment_time": "2026-11-10T10:00:00+00:00",
    "message": "Your appointment with Dr. Rajesh Varma for Panchakarma Consultation has been successfully confirmed for Tuesday, November 10 at 10:00 AM. Your confirmation ID is AYUR-7291."
  }
  ```

---

## 4. Telephony & Webhooks

### Twilio Incoming Call Webhook
- **Endpoint:** `POST /api/v1/telephony/incoming-call`
- **Headers:** `Content-Type: application/x-www-form-urlencoded`
- **Response (200 OK):**
  ```xml
  <Response>
    <Say voice="Polly.Aditi" language="en-IN">Namaste and welcome to Sree Kerala Ayurvedic Clinic. Connecting you to our Ayurvedic voice receptionist.</Say>
    <Connect>
      <Stream url="wss://your-ngrok.ngrok-free.app/api/v1/telephony/media-stream/c1111111-..." />
    </Connect>
  </Response>
  ```

### ElevenLabs Post-Call Webhook
- **Endpoint:** `POST /api/v1/webhooks/elevenlabs-post-call`
- **Request Body:**
  ```json
  {
    "call_id": "conv_987654321",
    "call_sid": "CA1234567890abcdef",
    "clinic_id": "c1111111-...",
    "caller_phone": "+919876543210",
    "duration_secs": 142,
    "recording_url": "https://api.elevenlabs.io/recordings/conv_987654321.mp3",
    "transcript": [
      {"role": "agent", "message": "Namaste! Welcome to Sree Kerala Ayurvedic Clinic."},
      {"role": "user", "message": "I'd like to book with Dr. Varma."}
    ],
    "analysis": {
      "transcript_summary": "Patient booked Panchakarma appointment.",
      "sentiment": "positive"
    }
  }
  ```
- **Response (200 OK):** `{"status": "success", "message": "Call log and transcript updated successfully."}`

---

## 5. Analytics & Dashboard

- `GET /api/v1/analytics/dashboard` - Aggregated statistics for stat cards and recent activity.
- `GET /api/v1/analytics/call-logs` - Paginated call log interactions with full transcripts.

