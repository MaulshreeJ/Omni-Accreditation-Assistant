# Starting the Omni Accreditation Copilot UI

## Quick Start

### Step 1: Start the Backend API

Open a terminal in the `accreditation_copilot` directory and run:

```bash
python run_api.py
```

You should see:
```
Starting Omni Accreditation Copilot API...
Server will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

The API is now running at **http://localhost:8000**

### Step 2: Install Frontend Dependencies

Open a **new terminal** in the `accreditation_copilot/frontend` directory and run:

```bash
npm install
```

This will install all required dependencies (Next.js, React, TailwindCSS, etc.)

### Step 3: Start the Frontend

In the same terminal, run:

```bash
npm run dev
```

You should see:
```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
- event compiled client and server successfully
```

The UI is now running at **http://localhost:3000**

### Step 4: Open the UI

Open your browser and navigate to:

**http://localhost:3000**

You should see the Omni Accreditation Copilot dashboard!

## Features Available

### 1. Query Panel (Top)
- **Framework Selection**: Choose NAAC or NBA
- **Criterion Input**: Enter criterion (e.g., "3.2.1")
- **Text Query**: Optional custom query
- **Voice Input**: Click microphone icon to use voice
- **File Upload**: Upload PDF/PNG/JPG documents
- **Run Audit Button**: Execute the audit

### 2. Audit Dashboard
- Compliance Status (Green/Yellow/Red)
- Confidence Score (0-100%)
- Coverage Ratio (0-100%)
- Evidence Count
- Cache Indicator

### 3. Evidence Viewer
- Interactive evidence cards
- Click to expand full text
- Source document and page number
- Reranker scores
- Evidence strength (Strong/Moderate/Weak)

### 4. Gap Analysis Panel
- Detected compliance gaps
- Severity levels (High/Medium/Low)
- Descriptions and recommendations

### 5. Metrics Panel
- Precision@8
- Recall@8
- F1 Score
- MRR (Mean Reciprocal Rank)
- Bar chart visualization

## API Endpoints

The backend exposes these endpoints:

- `GET /` - API info
- `GET /health` - Health check
- `POST /api/audit/run` - Run audit
- `GET /api/audit/cache` - Get cached audits
- `DELETE /api/audit/cache` - Clear cache
- `POST /api/upload` - Upload files
- `POST /api/upload/ingest` - Trigger ingestion
- `GET /api/metrics` - Get retrieval metrics

API documentation available at: **http://localhost:8000/docs**

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
pip install fastapi uvicorn python-multipart pydantic
```

**Problem**: Port 8000 already in use

**Solution**:
```bash
# Find and kill the process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Frontend Issues

**Problem**: `npm: command not found`

**Solution**: Install Node.js from https://nodejs.org/

**Problem**: Port 3000 already in use

**Solution**: The frontend will automatically use port 3001 if 3000 is busy

**Problem**: Voice input not working

**Solution**: Voice input requires:
- Chrome or Edge browser (best support)
- HTTPS or localhost
- Microphone permissions granted

## Testing the System

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy"}
```

### Test 2: Run Audit

```bash
curl -X POST http://localhost:8000/api/audit/run \
  -H "Content-Type: application/json" \
  -d '{"framework":"NAAC","criterion":"3.2.1"}'
```

### Test 3: Get Metrics

```bash
curl http://localhost:8000/api/metrics/
```

Expected response:
```json
{
  "precision": 0.469,
  "recall": 0.625,
  "f1": 0.536,
  "mrr": 1.000,
  "num_queries": 8,
  "top_k": 8
}
```

## System Requirements

### Backend
- Python 3.8+
- 4GB RAM minimum
- Internet connection (for model downloads on first run)

### Frontend
- Node.js 18+
- Modern browser (Chrome, Edge, Firefox, Safari)

## Environment Variables

### Backend (Optional)
Create `.env` file in `accreditation_copilot/`:

```bash
GROQ_API_KEY_1=your_key_here
GROQ_API_KEY_2=your_key_here
HF_TOKEN=your_token_here
```

### Frontend (Optional)
Create `.env.local` in `accreditation_copilot/frontend/`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Stopping the Servers

### Stop Backend
Press `Ctrl+C` in the terminal running the API

### Stop Frontend
Press `Ctrl+C` in the terminal running Next.js

## Next Steps

1. Upload institution documents via the UI
2. Run audits for different criteria
3. Explore evidence and gaps
4. View retrieval metrics
5. Check cached results for instant responses

## Support

For issues or questions, refer to:
- `UI_IMPLEMENTATION_GUIDE.md` - Complete implementation details
- `FINAL_STATUS_REPORT.md` - System status and capabilities
- API docs at http://localhost:8000/docs

---

**Status**: Ready to Run
**Last Updated**: March 6, 2026
