"""
Run the FastAPI server
"""
import uvicorn

if __name__ == "__main__":
    print("Starting Omni Accreditation Copilot API...")
    print("Server will be available at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop\n")
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
