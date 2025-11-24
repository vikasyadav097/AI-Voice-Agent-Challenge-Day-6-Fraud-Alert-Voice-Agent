# Setup Guide

## Quick Setup (5 minutes)

### 1. Get API Keys

You'll need three API keys:

1. **Murf AI API Key**
   - Sign up at https://murf.ai/
   - Get your API key from the dashboard

2. **Deepgram API Key**
   - Sign up at https://deepgram.com/
   - Get your API key from console

3. **Google AI API Key**
   - Go to https://ai.google.dev/
   - Create a project and get API key

### 2. Install Dependencies

**Backend:**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -e .
```

**Frontend:**
```bash
cd frontend
npm install
```

### 3. Configure Environment

**backend/.env.local:**
```env
LIVEKIT_URL=ws://127.0.0.1:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
GOOGLE_API_KEY=your_google_api_key_here
MURF_API_KEY=your_murf_api_key_here
DEEPGRAM_API_KEY=your_deepgram_api_key_here
```

**frontend/.env.local:**
```env
NEXT_PUBLIC_LIVEKIT_URL=ws://127.0.0.1:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```

### 4. Run the Application

**Terminal 1 - LiveKit Server:**
```bash
./livekit-server.exe --dev
```

**Terminal 2 - Backend:**
```bash
cd backend
.venv\Scripts\activate
python src/agent.py dev
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

### 5. Test It Out

1. Open http://localhost:3000
2. Click "Connect"
3. Say "Hello"
4. Say "I want to learn mode"
5. Start learning!

## Troubleshooting

**Port already in use?**
- Kill the process using that port
- Or change the port in .env.local files

**Agent not responding?**
- Check all three terminals are running
- Verify API keys are correct
- Check browser console for errors

**No audio?**
- Grant microphone permissions
- Check audio output device
- Verify Murf API key is valid

## Need Help?

Check the main README.md for detailed documentation.
