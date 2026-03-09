"""
Chatbot Router - AI-powered help assistant
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models.model_manager import get_model_manager

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    history: list = []

class ChatResponse(BaseModel):
    response: str

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    AI-powered chatbot endpoint for helping users navigate the system.
    """
    try:
        model_manager = get_model_manager()
        groq_client = model_manager.get_groq_client()
        
        # System prompt with knowledge about the project
        system_prompt = """You are Omni Assistant, a helpful AI guide for the Omni Accreditation Copilot platform. 

**About the Platform:**
Omni is an AI-powered accreditation audit system for NAAC and NBA frameworks that helps educational institutions analyze compliance and get recommendations.

**Key Features:**
1. **Dashboard**: Upload SSR PDFs and run audits
2. **Upload & Ingest**: Upload PDFs (max 20MB), click "Ingest Files"
3. **Run Audit**: Select framework (NAAC/NBA), criterion, click "Run Audit"
4. **Results**: Shows confidence score (0-100%), grade (A+ to D), coverage, recommendations
5. **History**: Past audits and progress tracking
6. **Metrics**: Performance analytics
7. **Top Universities**: Learn from top-ranked institutions
8. **Profile**: Account info and stats
9. **Settings**: Customize preferences

**Scoring:**
- 75%+ = High (A+/A) - Excellent
- 50-75% = Moderate (B+/B) - Good
- 25-50% = Weak (C) - Needs work
- <25% = Insufficient (D) - Major gaps

**How to Improve:**
- Upload detailed data tables with numbers, dates, funding
- Include all required dimensions
- Provide complete documentation
- Follow recommendations after each audit

**Common Tasks:**
- Getting started: Upload PDF → Ingest → Select framework/criterion → Run Audit
- Understanding results: Check score, grade, coverage, recommendations
- Track progress: Use History and Metrics pages

Be friendly, concise, and helpful. Give step-by-step guidance. Keep responses short and actionable."""

        # Build conversation history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (last 5 messages for context)
        for msg in request.history[-5:]:
            messages.append(msg)
        
        # Add current user message
        messages.append({"role": "user", "content": request.message})
        
        # Get AI response from Groq (using faster model)
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Faster model for quick responses
            messages=messages,
            temperature=0.7,
            max_tokens=250,  # Reduced for faster responses
            top_p=0.9
        )
        
        bot_response = response.choices[0].message.content
        
        return ChatResponse(response=bot_response)
        
    except Exception as e:
        print(f"[CHATBOT ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")
