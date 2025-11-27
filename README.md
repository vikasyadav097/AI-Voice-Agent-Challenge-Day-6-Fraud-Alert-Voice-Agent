---

# 🔔 AI Voice Agent Challenge | Day 6: Fraud Alert Voice Agent
A real-time **Fraud Detection Voice Agent** built using **LiveKit Agents, Murf AI Falcon TTS, Deepgram STT, and Google Gemini**.
This AI agent calls customers, verifies identity (safely), and investigates suspicious transactions — all through natural conversation.

---

# 🌟 Key Features

## 🔍 Fraud Detection Capabilities

* **Customer Identity Verification**
  Secure, non-sensitive verification using preset security questions
* **Suspicious Transaction Review**
  Reads transactions clearly and confirms with the user in real time
* **Decision Handling**
  Marks transactions as **safe**, **fraudulent**, or **verification_failed**
* **Auto Database Updates**
  Writes results into `fraud_cases.json` with timestamps
* **Bank-grade Call Experience**
  Professional flow inspired by real-world fraud call workflows

---

# 🔐 Security Principles (Important!)

* Never requests: **Card number, PIN, CVV, password, or OTP**
* Only asks controlled, non-sensitive security questions
* 2 verification attempts maximum
* All cases use **fake/demo data**
* Clear audit trail maintained in JSON database

---

# ☎️ Full Call Flow

1. **Agent Introduction** – Identifies as SecureBank Fraud Department
2. **Name Collection** – Gets the customer’s name
3. **Case Loading** – Loads matching fraud case
4. **Verification** – Asks 1 security question
5. **Suspicious Transaction Details** – Reads out merchant, time, location, amount
6. **Customer Confirmation** – “Did you make this transaction?”
7. **Final Action**

   * If **Yes** → Mark safe
   * If **No** → Block the card + mark fraudulent
   * If verification fails → terminate call

---

# 🎙️ Voice & AI Integration

* **Murf AI Falcon TTS** → Natural Ryan voice (ultra-low latency)
* **Deepgram STT** → Fast voice-to-text
* **Gemini 2.5 Flash** → Reasoning + function calling
* **LiveKit WebRTC** → Real-time audio streaming

---

# 🚀 Quick Start Guide

## Prerequisites

* Python **3.11+**
* Node.js **18+**
* LiveKit Server
* API Keys:

  * Murf AI
  * Deepgram
  * Google Gemini

---

# 🛠️ Installation Steps

## 1️⃣ Clone Repository

```bash
git clone https://github.com/vikasyadav097/AI-Voice-Agent-Challenge-Day-6-Fraud-Alert-Voice-Agent
cd ten-days-of-voice-agents-2025
```

## 2️⃣ Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate       # Windows
source .venv/bin/activate    # Mac/Linux

pip install -r requirements.txt
```

## 3️⃣ Backend Environment Setup

Create `backend/.env.local`:

```env
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
DEEPGRAM_API_KEY=your_deepgram_key
GOOGLE_API_KEY=your_gemini_key
MURF_API_KEY=your_murf_key
```

## 4️⃣ Frontend Setup

```bash
cd ../frontend
npm install
```

## 5️⃣ Frontend Environment

Create `frontend/.env.local`:

```env
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
NEXT_PUBLIC_LIVEKIT_URL=ws://localhost:7880
```

---

# ▶️ Running the Application

## 1. Start LiveKit Server

```bash
cd ten-days-of-voice-agents-2025
./livekit-server.exe --dev       # Windows
./livekit-server --dev           # Mac/Linux
```

## 2. Start Fraud Agent

```bash
cd backend
.venv\Scripts\activate            # Windows
python src/agent.py dev
```

## 3. Start Frontend

```bash
cd frontend
npm run dev
```

## 4. Visit App

👉 [http://localhost:3000](http://localhost:3000)

---

# 💬 Sample Conversations

---

### ✅ Scenario 1: Transaction Confirmed Safe

```
Agent: "This is SecureBank Fraud Department. May I have your full name?"

You: "John Smith"

Agent: "Thank you. For security, what is your mother's maiden name?"

You: "Johnson"

Agent: "Thanks. We found a suspicious transaction:
- $1,247.99
- ABC Electronics Ltd
- Shanghai, China
- Nov 25, 2025, 3:42 PM

Did you make this purchase?"

You: "Yes"

Agent: "Great, marking this as legitimate. Your card remains active."
```

---

### ❌ Scenario 2: Fraud Confirmed

```
Agent: "For security, what city were you born in?"

You: "Boston"

Agent: "Suspicious transaction detected:
- $3,599.00
- Luxury Watches International
- Moscow, Russia

Did you make this transaction?"

You: "No"

Agent: "Thank you. We’ve blocked your card and issued a replacement."
```

---

### 🚫 Scenario 3: Verification Failed

```
Agent: "What is your favorite color?"

You: "Red"

Agent: "Doesn’t match. You have 1 attempt left."

You: "Green"

Agent: "Verification failed. Please visit your nearest branch."
```

---

# 📂 Project Structure

```
.
├── backend/
│   ├── src/
│   │   ├── agent.py
│   │   └── murf_tts.py
│   ├── .env.local
│   └── pyproject.toml
├── frontend/
│   ├── app/
│   ├── components/
│   ├── .env.local
│   └── package.json
├── shared-data/
│   └── fraud_cases.json
├── challenges/
│   └── Day 6 Task.md
└── livekit-server.exe
```

---

# 🔧 Customization

## ➕ Add New Fraud Cases

Edit `shared-data/fraud_cases.json`:

```json
{
  "userName": "Your Name",
  "securityQuestion": "What is your pet's name?",
  "securityAnswer": "Fluffy",
  "cardEnding": "1234",
  "transactionAmount": "$999.99",
  "transactionName": "Suspicious Store",
  "transactionTime": "Nov 26, 2025 at 10:00 PM",
  "transactionLocation": "Unknown",
  "status": "pending_review"
}
```

## 🏦 Change Bank Name

Update system prompt in:
`backend/src/agent.py`

## 🎙️ Modify Voice Style

```python
tts=murf_tts.TTS(
    voice="en-US-ryan",
    style="Conversational",
)
```

---

# 📊 Viewing Results

Check updated outcomes in:
`shared-data/fraud_cases.json`

Each case logs:

* Verification results
* Final decision (safe / fraud / verification_failed)
* Timestamped audit trail

---

# 🛠️ Tech Stack

* **Backend** — Python 3.11, LiveKit Agents
* **Frontend** — Next.js 15, React, TypeScript
* **Voice** — Murf Falcon TTS, Deepgram STT
* **LLM** — Google Gemini 2.5 Flash
* **Real-time** — LiveKit WebRTC
* **Database** — JSON storage

---

# 🔒 Security Notes (Important)

* Demo ONLY — use fake data
* Do NOT implement with real card/customer data
* For production, ensure:

  * Encryption
  * Token-based auth
  * PCI DSS compliance
  * Secure infrastructure

---

# 📝 API Keys Required

* Murf AI
* Deepgram
* Google Gemini

---

# 📚 Learning Resources

* LiveKit Agents
* Murf API Docs
* Deepgram Docs
* Gemini API Docs

---

# 🤝 Contributing

Pull requests and forks are welcome!

---

# 📄 License

MIT License

---

# 🙏 Acknowledgments

Built for **Murf AI Voice Agent Challenge — Day 6**
Thanks to:

* LiveKit
* Murf AI
* Deepgram
* Google AI

---
| Day      | Status         |
| -------- | -------------- |
| Day 1    | ✅ Completed    |
| Day 2    | ✅ Completed    |
| Day 3    | ✅ Completed    |
| Day 4    | ✅ Completed    |
| Day 5    | ✅ Completed    |
| Day 6    | ✅ Completed    |
| Day 7–10 | 🔜 Coming soon |

