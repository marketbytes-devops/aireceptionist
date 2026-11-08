# ElevenLabs Conversational AI & Twilio Voice Setup Guide

This guide provides end-to-end instructions for configuring an autonomous AI Ayurvedic Voice Receptionist using **ElevenLabs Conversational AI** and **Twilio**, linked directly to the **AyurVoice SaaS** backend.

---

## 1. Local Webhook Tunneling (ngrok)

To allow Twilio and ElevenLabs cloud servers to reach your local FastAPI server:

1. Install and start ngrok:
   ```bash
   ngrok http 8000
   ```
2. Note your public forwarding URL, for example:
   ```text
   https://ayurvoice-demo.ngrok-free.app
   ```
3. Update your `.env` in `backend/`:
   ```env
   BASE_URL="https://ayurvoice-demo.ngrok-free.app"
   ```

---

## 2. ElevenLabs Conversational AI Agent Configuration

1. Log in to [ElevenLabs Conversational AI Console](https://elevenlabs.io/app/conversational-ai).
2. Click **Create Agent** -> **Blank Agent**.
3. **Agent Name**: `AyurVoice Ayurvedic Receptionist`
4. **Voice Selection**: Choose a warm, calm, professional voice (e.g. *Aria*, *Serena*, or *Ananya*).
5. **System Prompt**:
   ```markdown
   You are Priya, the autonomous AI voice receptionist for Sree Kerala Ayurvedic Clinic.
   Your clinic offers authentic Ayurvedic wellness, Panchakarma therapies, Nadi Pariksha (pulse diagnosis), and dietetic lifestyle consultations.

   Your Tone:
   - Begin conversations with a warm "Namaste! Welcome to Sree Kerala Ayurvedic Clinic."
   - Speak politely, concisely, and calmly.
   - Keep spoken answers brief and natural for telephony.

   Your Workflow:
   1. Inquire about the caller's wellness needs or treatment preference (Panchakarma, Pulse Diagnosis, General).
   2. When the caller asks for appointment availability, ALWAYS call the `check_availability` tool using the clinic_id and requested date/time.
   3. Once the caller agrees on a slot, ask for their full name and phone number.
   4. Call the `book_appointment` tool to confirm the reservation.
   5. Relay the booking confirmation code clearly to the caller.
   ```

---

## 3. Registering Custom Tools in ElevenLabs

### Tool 1: `check_availability`
In your ElevenLabs Agent dashboard under **Tools** -> **Add Tool**:
- **Tool Type**: `Webhook`
- **Name**: `check_availability`
- **Description**: `Checks doctor availability and open time slots for a given clinic and date.`
- **Method**: `POST`
- **URL**: `https://<YOUR-NGROK-DOMAIN>/api/v1/tools/check-availability`
- **Parameters**:
  | Parameter | Type | Required | Description |
  |---|---|---|---|
  | `clinic_id` | string (UUID) | Yes | The clinic's unique ID |
  | `date_time` | string | Yes | Requested date/time, e.g. "2026-11-10T10:00:00" |
  | `doctor_name` | string | No | Optional doctor name, e.g. "Dr. Varma" |
  | `treatment_type` | string | No | Treatment category, e.g. "Panchakarma" |

### Tool 2: `book_appointment`
- **Tool Type**: `Webhook`
- **Name**: `book_appointment`
- **Description**: `Atomically books an appointment and schedules confirmation notification.`
- **Method**: `POST`
- **URL**: `https://<YOUR-NGROK-DOMAIN>/api/v1/tools/book-appointment`
- **Parameters**:
  | Parameter | Type | Required | Description |
  |---|---|---|---|
  | `clinic_id` | string (UUID) | Yes | The clinic's unique ID |
  | `patient_name` | string | Yes | Full name of the patient |
  | `patient_phone` | string | Yes | Patient phone with country code |
  | `appointment_time` | string | Yes | Confirmed ISO datetime string |
  | `doctor_name` | string | No | Doctor name |
  | `treatment_type` | string | No | Treatment type |

---

## 4. ElevenLabs Post-Call Webhook

To automatically store call duration, audio recording, and transcripts in AyurVoice:
1. In ElevenLabs Agent settings, scroll to **Post-Call Webhook**.
2. Set URL to:
   ```text
   https://<YOUR-NGROK-DOMAIN>/api/v1/webhooks/elevenlabs-post-call
   ```
3. Set Method to `POST`.
4. Check **Include Transcript** and **Include Audio Recording URL**.

---

## 5. Twilio Voice Configuration

1. In the [Twilio Console](https://console.twilio.com), go to **Phone Numbers** -> **Manage** -> **Active numbers**.
2. Select your clinic's phone number.
3. Under **Voice & Fax**:
   - **A CALL COMES IN**: Select `Webhook`
   - **URL**: `https://<YOUR-NGROK-DOMAIN>/api/v1/telephony/incoming-call`
   - **HTTP METHOD**: `HTTP POST`
4. Save the configuration.

Now, whenever a patient dials the clinic number:
1. Twilio calls AyurVoice's `/api/v1/telephony/incoming-call`.
2. AyurVoice generates TwiML connecting the call to the ElevenLabs voice bridge.
3. The patient speaks naturally, tools execute dynamically against PostgreSQL, and bookings appear instantly on the admin dashboard!

