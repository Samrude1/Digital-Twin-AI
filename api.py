import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from agent_logic import Me

# Security: Rate Limiter (5 requests per minute, max 50 requests per day per IP)
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Sami Rautanen AI Clone API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration - strict origin regex restricted to verified deployment domains
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://(portfolio[a-zA-Z0-9-]*|sami-rautanen[a-zA-Z0-9-]*)\.vercel\.app|https://(www\.)?samirautanen\.fi|http://localhost:3000",
    allow_credentials=True,
    allow_methods=["GET", "POST", "HEAD", "OPTIONS"],
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
    role: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., max_length=2000)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)


@app.api_route("/", methods=["GET", "HEAD"])
def read_root():
    return {"status": "ok", "agent": "Sami Rautanen AI Clone"}


@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    """Health check endpoint for monitoring services"""
    return {"status": "healthy"}


@app.post("/chat")
@limiter.limit("5/minute")
@limiter.limit("50/day")
def chat_endpoint(req: ChatRequest, request: Request):
    if not my_agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")

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
