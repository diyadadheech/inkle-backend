# Inkle Multi-Agent Tourism (AI Intern assignment)

## Setup
1. Create a virtual environment:
   python -m venv venv
   source venv/bin/activate   # on Windows: venv\Scripts\activate

2. Install:
   pip install -r requirements.txt

3. Run:
   uvicorn app.main:app --reload --port 8000

4. Test:
   POST http://127.0.0.1:8000/plan
   Body (JSON): {"text": "I'm going to Bangalore, what is the temperature and places to visit?"}

5. Example cURL:
   curl -X POST "http://127.0.0.1:8000/plan" -H "Content-Type: application/json" -d '{"text":"I am going to Bangalore, what is the temperature there?"}'
