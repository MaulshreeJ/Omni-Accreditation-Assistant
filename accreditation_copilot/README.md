# 🎓 Omni Accreditation Copilot

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![Next.js](https://img.shields.io/badge/next.js-14+-black.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)

**AI-Powered Accreditation Intelligence for NAAC and NBA Frameworks**

[Quick Start](#-quick-start) • [Features](#-features) • [Documentation](#-documentation) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Usage Guide](#-usage-guide)
- [Theme System](#-theme-system)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

Omni Accreditation Copilot is an intelligent system that helps educational institutions prepare for NAAC (National Assessment and Accreditation Council) and NBA (National Board of Accreditation) assessments. It uses advanced AI to analyze institutional evidence, identify gaps, and provide actionable recommendations.

### Key Capabilities

✅ **Automated Compliance Auditing** - Run audits against NAAC/NBA criteria  
✅ **Evidence Analysis** - Analyze institutional documents and identify gaps  
✅ **Smart Recommendations** - Get actionable steps to improve grades  
✅ **Multimodal Input** - Text, voice, and file upload support  
✅ **Beautiful UI** - Modern glassmorphism design with 3 theme options  
✅ **Caching System** - Fast results with intelligent caching  

---

## ✨ Features

### 🎯 Core Features

| Feature | Description |
|---------|-------------|
| **Dual Retrieval** | Combines framework guidelines with institutional evidence |
| **Confidence Scoring** | Calculates compliance confidence with dimension coverage |
| **Gap Detection** | Identifies missing evidence and weak areas |
| **Evidence Grounding** | Links recommendations to specific evidence chunks |
| **Query Expansion** | Enhances queries for better retrieval |
| **Audit Caching** | Speeds up repeated audits with smart caching |

### 🎨 UI Features

| Feature | Description |
|---------|-------------|
| **3 Theme Options** | Quiet Night, Morning Light, Rainy Afternoon |
| **Voice Input** | Web Speech API integration |
| **File Upload** | PDF, PNG, JPG support |
| **Real-time Audit** | Live progress indicators |
| **Interactive Dashboard** | Visual metrics and charts |
| **Responsive Design** | Works on desktop and mobile |

### 🔧 Technical Features

| Feature | Description |
|---------|-------------|
| **FastAPI Backend** | High-performance async API |
| **Next.js Frontend** | React with TypeScript |
| **FAISS + BM25** | Hybrid retrieval system |
| **Groq LLM** | Fast inference with Llama models |
| **SQLite Metadata** | Efficient metadata storage |
| **Property-Based Testing** | Comprehensive test coverage |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn
- Virtual environment (venv)

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd accreditation_copilot

# 2. Set up Python virtual environment
python -m venv ../venv
../venv/Scripts/activate  # Windows
source ../venv/bin/activate  # Linux/Mac

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install frontend dependencies
cd frontend
npm install
cd ..

# 5. Set up environment variables
copy .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### Running the Application

#### Option 1: Using Startup Scripts (Recommended)

**Terminal 1 - Backend:**
```powershell
cd accreditation_copilot
.\scripts\RESTART_BACKEND.bat
```

**Terminal 2 - Frontend:**
```powershell
cd accreditation_copilot
.\scripts\START_FRONTEND.bat
```

#### Option 2: Manual Start

**Backend:**
```bash
cd accreditation_copilot
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd accreditation_copilot/frontend
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📁 Project Structure

```
accreditation_copilot/
├── 📱 frontend/              # Next.js frontend application
│   ├── app/                  # Next.js app directory
│   ├── components/           # React components
│   └── public/               # Static assets
│
├── 🔧 api/                   # FastAPI backend
│   ├── main.py              # API entry point
│   ├── routers/             # API route handlers
│   └── error_handler.py     # Error handling
│
├── 🧠 Core Modules/
│   ├── audit/               # Audit pipeline
│   ├── retrieval/           # Dual retrieval system
│   ├── scoring/             # Confidence & coverage scoring
│   ├── analysis/            # Gap detection & grounding
│   ├── synthesis/           # Report generation
│   └── validation/          # Report validation
│
├── 💾 Data & Storage/
│   ├── data/                # Raw docs, chunks, metadata
│   ├── indexes/             # FAISS indexes
│   ├── cache/               # Audit cache
│   └── audit_results/       # Audit outputs
│
├── 🛠️ Utilities/
│   ├── ingestion/           # Document processing
│   ├── models/              # Model management
│   ├── criteria/            # Criterion registry
│   ├── utils/               # Helper functions
│   └── security/            # Security utilities
│
├── 📜 Scripts/
│   ├── RESTART_BACKEND.bat  # Start backend
│   ├── START_FRONTEND.bat   # Start frontend
│   ├── start_servers.bat    # Start both
│   ├── demos/               # Demo scripts
│   └── utils/               # Utility scripts
│
├── 🧪 tests/                # Test files
├── 📚 docs/                 # Documentation
├── 📋 requirements.txt      # Python dependencies
├── 🔐 .env.example          # Environment template
└── 📖 README.md             # This file
```

---

## 📖 Usage Guide

### 1. Upload Institutional Documents

1. Click the **Upload** button (📤) in the query panel
2. Select PDF, PNG, or JPG files
3. Click **Ingest Files** to process them
4. Wait for "Files ingested successfully!" message

### 2. Run an Audit

1. Select **Framework**: NAAC or NBA
2. Enter **Criterion**: e.g., `3.2.1` for NAAC or `C5` for NBA
3. (Optional) Enter a custom query or use voice input (🎤)
4. Click **Run Audit**
5. Wait for results (5-15 seconds)

### 3. Review Results

The dashboard shows:

- **Compliance Status**: Compliant, Partial, Weak, or No Evidence
- **Confidence Score**: Overall confidence (0-100%)
- **Coverage Ratio**: Dimension coverage (0-100%)
- **Evidence Count**: Number of evidence chunks found

### 4. Analyze Recommendations

The **Roadmap to A+ Grade** panel provides:

- ✅ Actionable recommendations with priority levels
- ✅ Specific action items for each recommendation
- ✅ Expected impact on your grade
- ✅ Timeline estimates

### 5. Explore Evidence

The **Evidence Viewer** shows:

- Source documents
- Relevant text chunks
- Confidence scores
- Dimension coverage

---

## 🎨 Theme System

Omni features 3 beautiful themes to match your work environment:

### 🌟 Quiet Night (Default)
- **Best for**: Night work, focused coding
- **Colors**: Deep indigo with neon cyan & pink
- **Mood**: Modern, tech-forward, energetic

### ☀️ Morning Light
- **Best for**: Morning sessions, positive energy
- **Colors**: Warm golden yellow and cream
- **Mood**: Optimistic, fresh, welcoming

### 🌧️ Rainy Afternoon
- **Best for**: Afternoon work, reduced distractions
- **Colors**: Soft gray and muted blue
- **Mood**: Calm, professional, serene

**How to Switch Themes:**
1. Look for the theme icon in the sidebar (⭐/☀️/☁️)
2. Click to open the theme menu
3. Select your preferred theme
4. Theme saves automatically!

📚 **Learn More**: [Theme System Guide](docs/THEME_SYSTEM_GUIDE.md)

---

## 🔌 API Documentation

### Audit Endpoint

**POST** `/api/audit/run`

Run an audit for a specific criterion.

**Request Body:**
```json
{
  "framework": "NAAC",
  "criterion": "3.2.1",
  "query": "Optional custom query"
}
```

**Response:**
```json
{
  "criterion": "3.2.1",
  "framework": "NAAC",
  "compliance_status": "Partial",
  "confidence_score": 0.07,
  "coverage_ratio": 1.0,
  "dimensions_covered": ["funding_amount", "project_count", "funding_agencies"],
  "dimensions_missing": [],
  "evidence_count": 10,
  "evidence": [...],
  "gaps": [...],
  "recommendations": [...],
  "explanation": "...",
  "timestamp": "2024-01-01T00:00:00",
  "cached": false
}
```

### Upload Endpoint

**POST** `/api/upload/`

Upload institutional documents.

**Request:** Multipart form data with files

**Response:**
```json
{
  "message": "Files uploaded successfully",
  "files": ["file1.pdf", "file2.pdf"],
  "count": 2
}
```

### Ingest Endpoint

**POST** `/api/upload/ingest`

Process uploaded files and build indexes.

**Response:**
```json
{
  "message": "Files ingested successfully",
  "chunks_created": 25,
  "indexes_built": ["FAISS", "BM25", "SQLite"]
}
```

📚 **Full API Docs**: http://localhost:8000/docs (when running)

---

## 💻 Development

### Backend Development

```bash
# Activate virtual environment
../venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Run backend with auto-reload
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Code Style

**Python:**
- Follow PEP 8
- Use type hints
- Document functions with docstrings

**TypeScript/React:**
- Use TypeScript strict mode
- Follow React best practices
- Use functional components with hooks

---

## 🧪 Testing

### Run All Tests

```bash
# Python tests
cd accreditation_copilot
pytest tests/

# Specific test file
pytest tests/test_audit_flow.py

# With coverage
pytest --cov=. tests/
```

### Available Tests

| Test File | Description |
|-----------|-------------|
| `test_audit_flow.py` | End-to-end audit pipeline |
| `test_audit_response.py` | API response structure |
| `test_dimension_check.py` | Dimension coverage |
| `test_groq_connection.py` | LLM connectivity |
| `test_institution_retrieval.py` | Institution evidence retrieval |
| `test_integration.py` | Integration tests |
| `test_retrieval_fields.py` | Retrieval field validation |
| `test_stability_fixes.py` | Stability fixes validation |

### Demo Scripts

```bash
# Cache system demo
python scripts/demos/demo_cache_system.py

# Phase 6 complete demo
python scripts/demos/demo_phase6_complete.py

# Phase E tracing demo
python scripts/demos/demo_phase_e_tracing.py
```

---

## 🔧 Troubleshooting

### Common Issues

#### Backend won't start

**Error:** `No module named 'fastapi'`

**Solution:**
```bash
# Ensure virtual environment is activated
../venv/Scripts/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### Frontend won't start

**Error:** `Cannot find module 'next'`

**Solution:**
```bash
cd frontend
npm install
```

#### Port already in use

**Error:** `Address already in use: 8000`

**Solution:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

#### No recommendations showing

**Cause:** Backend not sending all required fields

**Solution:**
1. Restart backend with updated code
2. Clear browser cache (Ctrl+Shift+R)
3. Check browser console for errors

#### Theme not applying

**Cause:** localStorage issue or CSS not loaded

**Solution:**
1. Clear browser cache
2. Check browser console for errors
3. Verify `globals.css` is loaded

### Getting Help

1. Check [Documentation](#-documentation)
2. Review [API Docs](http://localhost:8000/docs)
3. Check browser console for errors
4. Check backend logs for errors

---

## 📚 Documentation

### User Guides

- [Quick Start Guide](docs/QUICK_FIX_GUIDE.md)
- [Data Ingestion Guide](docs/DATA_INGESTION_GUIDE.md)
- [Theme System Guide](docs/THEME_SYSTEM_GUIDE.md)
- [Theme Preview](docs/THEME_PREVIEW.md)

### Technical Documentation

- [Project Structure](docs/PROJECT_STRUCTURE.md)
- [API Documentation](http://localhost:8000/docs)
- [Retrieval System](docs/RETRIEVAL_SYSTEM_COMPLETE.md)
- [Scoring Pipeline](docs/PHASE6_SUMMARY.md)
- [Cache System](docs/CACHE_SYSTEM_COMPLETE.md)

### Implementation Guides

- [UI Implementation](docs/UI_IMPLEMENTATION_GUIDE.md)
- [Stability Fixes](docs/STABILITY_FIXES_COMPLETE.md)
- [Recommendations Fix](docs/RECOMMENDATIONS_FIX.md)
- [Evidence Display Fix](docs/EVIDENCE_DISPLAY_FIX.md)

### Reference

- [Multi-Query Retrieval](docs/MULTI_QUERY_QUICK_REFERENCE.md)
- [RRF Quick Reference](docs/RRF_QUICK_REFERENCE.md)
- [Stability Quick Ref](docs/STABILITY_QUICK_REF.md)

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Test your changes**
   ```bash
   pytest tests/
   npm run build  # for frontend changes
   ```
5. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Code Guidelines

- Write clear, descriptive commit messages
- Add tests for new features
- Update documentation as needed
- Follow existing code style
- Keep PRs focused and small

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **NAAC** - National Assessment and Accreditation Council
- **NBA** - National Board of Accreditation
- **Groq** - Fast LLM inference
- **FAISS** - Efficient similarity search
- **Next.js** - React framework
- **FastAPI** - Modern Python web framework

---

## 📞 Support

Need help? Here's how to get support:

- 📖 Check the [Documentation](#-documentation)
- 🐛 Report bugs via GitHub Issues
- 💡 Request features via GitHub Issues
- 📧 Contact the team at [email]

---

<div align="center">

**Made with ❤️ for Educational Institutions**

[⬆ Back to Top](#-omni-accreditation-copilot)

</div>
