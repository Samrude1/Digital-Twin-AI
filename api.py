# api.py
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from agent_logic import Me
import os
import google.generativeai as genai

# Security: Rate Limiter (5 requests per minute per IP)
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# DIAGNOSTIC: Check available models
# (Disabled for production speed - avoids blocking startup)
# try:
#     api_key = os.environ.get("GEMINI_API_KEY")
#     if api_key:
#         print(f"DIAGNOSTIC: Key found (starts with {api_key[:4]}). Listing models...")
#         genai.configure(api_key=api_key)
#         models = list(genai.list_models())
#         print("DIAGNOSTIC: Available Models:")
#         for m in models:
#             if 'generateContent' in m.supported_generation_methods:
#                 print(f" - {m.name}")
#     else:
#         print("DIAGNOSTIC: GEMINI_API_KEY not found in env.")
# except Exception as e:
#     print(f"DIAGNOSTIC ERROR: {e}")

# Allow CORS for development and production
origins = [
    "http://localhost:3000",
    "https://portfolio-seven-rho-74yt50nw74.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Agent
try:
    my_agent = Me()
    print("Agent initialized successfully.")
except Exception as e:
    print(f"Failed to initialize agent: {e}")
    my_agent = None

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []

@app.get("/")
@app.head("/")  # UptimeRobot often uses HEAD requests
def read_root():
    return {"status": "ok", "agent": "Sami Rautanen AI Clone"}

@app.get("/health")
@app.head("/health")
def health_check():
    """Health check endpoint for monitoring services"""
    return {"status": "healthy"}

@app.post("/chat")
@limiter.limit("5/minute")   # Short term: 5 messages per minute
@limiter.limit("50/day")     # Long term: 50 messages per day per IP (protection!)
def chat_endpoint(req: ChatRequest, request: Request):
    if not my_agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    # Convert Pydantic models to dicts for the agent logic
    history_dicts = [{"role": m.role, "content": m.content} for m in req.history]
    
    try:
        response_text = my_agent.chat(req.message, history_dicts)
        return {"reply": response_text}
    except Exception as e:
        print(f"Error in chat processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
