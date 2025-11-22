# app/main.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
from .agents import ParentAgent
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Inkle Tourism Multi-Agent")

# ⭐ ADD CORS so React frontend can call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # allow all frontends (React)
    allow_credentials=True,
    allow_methods=["*"],      # GET, POST, OPTIONS, etc.
    allow_headers=["*"],
)

parent = ParentAgent()

class QueryIn(BaseModel):
    text: str

# Original endpoint (optional)
@app.post("/plan")
async def plan(req: QueryIn):
    result = await parent.handle(req.text)
    return result

# NEW chatbot-style endpoint
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()

    # If raw string is sent, treat entire body as message
    if isinstance(data, str):
        text = data
    else:
        text = data.get("text", "")

    result = await parent.handle(text)

    if result.get("error"):
        return {"reply": result["message"]}

    # Weather only
    if "weather" in result and "places" not in result:
        w = result["weather"]
        temp = w.get("temperature_c")
        prob = w.get("precipitation_probability_percent")
        return {
            "reply": f"The temperature is {temp}°C with {prob}% chance of rain."
        }

    # Places only
    if "places" in result and "weather" not in result:
        places = result["places"]
        if not places:
            return {"reply": "Sorry, I couldn't find tourist places."}
        reply = "Here are some places you can visit:\n" + "\n".join(f"- {p}" for p in places)
        return {"reply": reply}

    # Both weather + places
    return {"reply": result.get("message", "")}

@app.get("/health")
async def health():
    return {"status": "ok"}
