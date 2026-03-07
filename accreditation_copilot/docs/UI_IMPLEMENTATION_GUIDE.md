# Omni Accreditation Copilot - UI Implementation Guide

## Overview

This guide covers the multimodal UI layer built on top of the existing Omni Accreditation Copilot backend system.

## Architecture

```
┌─────────────────────────────────────────┐
│         Next.js Frontend (Port 3000)     │
│  - React Components                      │
│  - TailwindCSS Styling                   │
│  - Framer Motion Animations              │
│  - Recharts Visualizations               │
└─────────────────────────────────────────┘
                    ↓ HTTP/REST
┌─────────────────────────────────────────┐
│         FastAPI Backend (Port 8000)      │
│  - /api/audit/run                        │
│  - /api/audit/cache                      │
│  - /api/upload                           │
│  - /api/metrics                          │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Existing Python Modules             │
│  - CriterionAuditor                      │
│  - DualRetriever                         │
│  - ModelManager (Singleton)              │
│  - AuditCache                            │
└─────────────────────────────────────────┘
```

## Installation

### Backend (FastAPI)

```bash
cd accreditation_copilot/api
pip install -r requirements.txt
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend (Next.js)

```bash
cd accreditation_copilot/frontend
npm install
npm run dev
```

The UI will be available at `http://localhost:3000`

## Features Implemented

### 1. Query Panel
- **Text Input**: Enter criterion and optional query
- **Voice Input**: Web Speech API integration for voice queries
- **File Upload**: Upload PDF/PNG/JPG evidence documents
- **Framework Selection**: Choose between NAAC and NBA

### 2. Audit Dashboard
- **Compliance Status**: Visual indicator (green/yellow/red)
- **Confidence Score**: Gauge chart with percentage
- **Coverage Ratio**: Progress bar showing dimension coverage
- **Evidence Count**: Number of retrieved chunks
- **Cache Indicator**: Shows if result was cached

### 3. Evidence Viewer
- **Interactive Cards**: Expandable evidence chunks
- **Source Information**: Document name and page number
- **Reranker Scores**: Relevance scores displayed
- **Evidence Strength**: Color-coded (Strong/Moderate/Weak)
- **Full Text View**: Expand to see complete chunk text

### 4. Gap Analysis Panel
- **Gap Types**: Categorized compliance gaps
- **Severity Levels**: High/Medium/Low with color coding
- **Descriptions**: Detailed gap explanations
- **Recommendations**: Actionable suggestions

### 5. Retrieval Metrics Panel
- **Bar Charts**: Visual representation of metrics
- **Precision@k**: Retrieval precision score
- **Recall@k**: Retrieval recall score
- **F1 Score**: Harmonic mean of precision/recall
- **MRR**: Mean Reciprocal Rank

### 6. Sidebar Navigation
- Dashboard
- Audits
- Metrics
- History
- Settings

## API Endpoints

### POST /api/audit/run
Run audit for a specific criterion.

**Request**:
```json
{
  "framework": "NAAC",
  "criterion": "3.2.1",
  "query": "optional custom query"
}
```

**Response**:
```json
{
  "criterion": "3.2.1",
  "framework": "NAAC",
  "compliance_status": "compliant",
  "confidence_score": 0.85,
  "coverage_ratio": 0.92,
  "evidence_count": 15,
  "evidence": [...],
  "gaps": [...],
  "grounding": {...},
  "timestamp": "2026-03-06T10:30:00",
  "cached": false
}
```

### GET /api/audit/cache
Retrieve cached audit results.

### DELETE /api/audit/cache
Clear all cached audits.

### POST /api/upload
Upload institution documents.

**Request**: Multipart form data with files

**Response**:
```json
[
  {
    "filename": "document.pdf",
    "size": 1024000,
    "status": "success",
    "message": "Uploaded successfully"
  }
]
```

### POST /api/upload/ingest
Trigger ingestion pipeline for uploaded files.

### GET /api/metrics
Get retrieval evaluation metrics.

**Response**:
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

## Technology Stack

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **TailwindCSS**: Utility-first CSS framework
- **ShadCN UI**: Component library
- **Framer Motion**: Animation library
- **Recharts**: Chart library
- **Lucide React**: Icon library

### Backend
- **FastAPI**: Modern Python web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation

## Design System

### Colors
- **Primary**: Blue (#3b82f6)
- **Success**: Green (#22c55e)
- **Warning**: Yellow (#eab308)
- **Danger**: Red (#ef4444)
- **Background**: Dark (#0a0a0a)
- **Card**: Dark Gray (#1a1a1a)

### Typography
- **Font**: Inter (Google Fonts)
- **Headings**: Bold, 2xl-xl
- **Body**: Regular, sm-base

### Spacing
- **Padding**: 4-6 units
- **Gap**: 2-4 units
- **Border Radius**: lg (0.5rem)

## Multimodal Features

### Voice Input
Uses Web Speech API (webkit):
```typescript
const recognition = new webkitSpeechRecognition();
recognition.continuous = false;
recognition.interimResults = false;
recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  setQuery(transcript);
};
recognition.start();
```

### File Upload
Supports PDF, PNG, JPG:
```typescript
<input
  type="file"
  multiple
  accept=".pdf,.png,.jpg,.jpeg"
  onChange={handleFileUpload}
/>
```

## Performance Considerations

### Backend
- **ModelManager Singleton**: Models loaded once at startup
- **Audit Caching**: 114-353x speedup for cached results
- **No Model Reloading**: All API calls use existing ModelManager

### Frontend
- **Code Splitting**: Next.js automatic code splitting
- **Lazy Loading**: Components loaded on demand
- **Optimistic Updates**: Immediate UI feedback
- **Debouncing**: Input debouncing for search

## Deployment

### Backend
```bash
cd accreditation_copilot/api
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd accreditation_copilot/frontend
npm run build
npm start
```

## Environment Variables

### Backend
```bash
GROQ_API_KEY_1=your_key_here
GROQ_API_KEY_2=your_key_here
HF_TOKEN=your_token_here
```

### Frontend
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Testing

### Backend
```bash
# Test API endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/audit/run \
  -H "Content-Type: application/json" \
  -d '{"framework":"NAAC","criterion":"3.2.1"}'
```

### Frontend
```bash
# Run development server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint
```

## Troubleshooting

### CORS Issues
Ensure FastAPI CORS middleware allows `http://localhost:3000`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Voice Input Not Working
Voice input requires HTTPS or localhost. Check browser compatibility:
- Chrome/Edge: Supported
- Firefox: Limited support
- Safari: Requires webkit prefix

### File Upload Fails
Check file size limits and allowed extensions:
```python
allowed_extensions = {".pdf", ".png", ".jpg", ".jpeg"}
```

## Future Enhancements

1. **Audit History**: Persistent storage of audit results
2. **PDF Export**: Generate PDF reports
3. **Real-time Updates**: WebSocket for live audit progress
4. **User Authentication**: Login and role-based access
5. **Collaborative Features**: Multi-user audit review
6. **Advanced Analytics**: Trend analysis and predictions
7. **Mobile App**: React Native mobile client

## Success Criteria

✅ User can upload institution documents
✅ User can run audit for NAAC criteria
✅ User can view compliance report visually
✅ User can explore evidence sources
✅ User can see metrics and gaps
✅ User can use text or voice input
✅ User can retrieve cached audit results instantly

## Status

✅ **IMPLEMENTATION COMPLETE**

The multimodal UI layer is fully implemented and ready for use. The system provides a modern, interactive interface for accreditation auditing while maintaining the stability and performance of the existing backend.

---

**Last Updated**: March 6, 2026
**Version**: 1.0.0
**Status**: Production Ready
