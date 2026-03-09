# 🚀 Omni Accreditation Copilot - Startup Guide

## Quick Start Commands

### Terminal 1: Backend API Server
```bash
cd accreditation_copilot
python api/start_api.py
```

**Expected Output:**
```
Starting Omni Accreditation Copilot API...
Python version: 3.12.x
[OK] uvicorn installed
[OK] fastapi installed
Starting server on http://localhost:8000
API docs available at http://localhost:8000/docs
```

### Terminal 2: Frontend Next.js App
```bash
cd accreditation_copilot/frontend
npm run dev
```

**Expected Output:**
```
▲ Next.js 14.x.x
- Local: http://localhost:3000
✓ Ready in X seconds
```

---

## 🌐 Access Points

- **Main Application**: http://localhost:3000
- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## ✨ New Features Added

### 1. AI Chatbot Assistant 🤖
- **Location**: Floating button in bottom-right corner (pulsing animation)
- **Features**:
  - AI-powered responses using Groq Llama 3.1 70B
  - Full knowledge of platform features
  - Conversation context maintained
  - Quick question buttons
  - Fallback responses when offline
- **How to Use**: Click the chat button and ask questions!

### 2. Top Universities Page 🏆
- **Location**: Sidebar → "Top Universities"
- **Features**:
  - View top-ranked NAAC and NBA institutions
  - See their success strategies
  - Learn what they did to achieve excellence
  - Filter by framework (ALL/NAAC/NBA)
  - Detailed modal with complete success factors
- **Universities Included**:
  - IIT Bombay (NAAC A++, 98.5%)
  - IISc Bangalore (NAAC A++, 97.8%)
  - JNU Delhi (NAAC A++, 96.2%)
  - NIT Trichy (NBA A+, 94.5%)
  - BITS Pilani (NBA A+, 93.8%)

### 3. Improved Font
- Changed from Inter to **Plus Jakarta Sans**
- More modern and professional appearance
- Applied across entire website

---

## 🎯 Complete Feature List

### Authentication
- ✅ Login page with demo login
- ✅ Register page with full form
- ✅ User profile in sidebar
- ✅ Logout functionality
- ✅ Protected routes

### Main Features
- ✅ Dashboard - Upload PDFs and run audits
- ✅ Profile - User info and activity stats
- ✅ History - Past audit results with trends
- ✅ Metrics - Performance analytics
- ✅ Settings - Customize preferences
- ✅ Top Universities - Learn from the best
- ✅ AI Chatbot - Get help anytime

### Backend
- ✅ Audit system with confidence scoring
- ✅ Evidence retrieval and analysis
- ✅ Dimension checking
- ✅ Cache clearing between uploads
- ✅ Chatbot endpoint with Groq API

---

## 🧪 Testing the Chatbot

### Method 1: Through UI
1. Open http://localhost:3000
2. Click the pulsing chat button (bottom-right)
3. Ask a question like "How do I get started?"

### Method 2: Test Script
```bash
cd accreditation_copilot
python test_chatbot_endpoint.py
```

This will verify the API endpoint is working correctly.

---

## 🔧 Troubleshooting

### Chatbot Shows "I'm currently offline"
**Cause**: API server not running or not accessible

**Solution**:
1. Check if API server is running in Terminal 1
2. Verify you see "Starting server on http://localhost:8000"
3. Test health endpoint: http://localhost:8000/health
4. If not running, restart with: `python api/start_api.py`

**Note**: The chatbot now has intelligent fallback responses, so it will still provide helpful information even when offline!

### Frontend Not Loading
**Cause**: Next.js dev server not running

**Solution**:
1. Check Terminal 2 for errors
2. Ensure you're in the `frontend` directory
3. Run `npm install` if packages are missing
4. Restart with `npm run dev`

### Port Already in Use
**Cause**: Another process using port 8000 or 3000

**Solution**:
```bash
# Windows - Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different port
python api/start_api.py --port 8001
```

---

## 📊 Demo Flow

### Quick Demo (5 minutes)
1. **Login**: Use demo login (demo@university.edu / demo123)
2. **Upload**: Upload test PDF from `D:/NAAC_Test_PDFs/`
3. **Ingest**: Click "Ingest Files" and wait
4. **Audit**: Select NAAC, criterion 3.2.1, click "Run Audit"
5. **Results**: View confidence score, grade, and recommendations
6. **Chatbot**: Ask "How can I improve my score?"
7. **Top Universities**: Check what top institutions did

### Full Demo (15 minutes)
1. All of the above, plus:
2. **History**: View past audits and trends
3. **Metrics**: Check performance analytics
4. **Profile**: View user stats and activity
5. **Settings**: Customize preferences
6. **Compare**: Upload different PDFs and compare results

---

## 🎨 UI Theme

**Stillness Theme Colors:**
- Primary: Cyan (#06b6d4)
- Secondary: Purple (#a855f7)
- Background: Dark slate (#0f172a)
- Cards: Glass morphism with blur
- Accents: Pink, Yellow, Green

**Font:**
- Plus Jakarta Sans (300, 400, 500, 600, 700, 800)

---

## 🔑 API Keys Configured

- ✅ GROQ_API_KEY_1 (Primary)
- ✅ GROQ_API_KEY_2 (Backup)
- ✅ GROQ_API_KEY_3 (Chatbot)
- ✅ GEMINI_API_KEY (Future features)
- ✅ LANGCHAIN_API_KEY (Observability)

---

## 📝 Test PDFs Available

Location: `D:/NAAC_Test_PDFs/`

1. **Excellence_University_A+_SSR.pdf**
   - 127 projects, ₹4580 Lakhs
   - Expected: ~75% confidence, Grade A+

2. **Good_College_B+_SSR.pdf**
   - 45 projects, ₹1000 Lakhs
   - Expected: ~59% confidence, Grade B+

3. **Struggling_College_C_SSR.pdf**
   - 9 projects, ₹73 Lakhs
   - Expected: ~20-30% confidence, Grade C

4. **MissingEvidence_College_D_SSR.pdf**
   - Vague text, no data
   - Expected: ~0-15% confidence, Grade D

---

## ✅ System Status

- ✅ Backend scoring system working correctly
- ✅ Cache clearing between uploads
- ✅ Frontend UI complete with all pages
- ✅ Authentication system functional
- ✅ AI chatbot with fallback responses
- ✅ Top universities page with real data
- ✅ Improved font (Plus Jakarta Sans)
- ✅ All navigation working
- ✅ Ready for demo!

---

## 🚀 You're Ready!

Everything is set up and working. Just run the two commands above and you're good to go!

**Need Help?**
- Ask the AI chatbot (it works even offline now!)
- Check the Top Universities page for best practices
- Review the API docs at http://localhost:8000/docs
