"""
Test script to verify chatbot endpoint is working
"""
import requests
import json

def test_chatbot():
    url = "http://localhost:8000/api/chatbot/chat"
    
    payload = {
        "message": "How do I get started?",
        "history": []
    }
    
    try:
        print("Testing chatbot endpoint...")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS!")
            print(f"Response: {data['response']}")
        else:
            print(f"\n❌ ERROR!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ CONNECTION ERROR!")
        print("API server is not running on http://localhost:8000")
        print("\nTo start the server, run:")
        print("  cd accreditation_copilot")
        print("  python api/start_api.py")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_chatbot()
