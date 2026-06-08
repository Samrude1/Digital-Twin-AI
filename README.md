# 🤖 Autonomous Career Digital Twin - Backend

> **Production-grade agentic AI system** powering an intelligent portfolio assistant. Not a chatbot—an autonomous agent with tool calling, guardrails, and real-world deployment.

[![Live Demo](https://img.shields.io/badge/Live-samirautanen.fi-blue)](https://samirautanen.fi)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal)](https://fastapi.tiangolo.com/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-Gemma_4_31B-blue)](https://openrouter.ai/)

---

## 📖 Overview

This is the **backend intelligence engine** for my portfolio's AI assistant—a production-deployed autonomous agent that represents me in conversations with visitors. It's not a simple Q&A bot; it's a **context-aware agent** with tool calling capabilities, email orchestration, and sophisticated guardrails.

**Live in production** on [samirautanen.fi](https://samirautanen.fi) handling real visitor inquiries.

### What Makes This Different

- ✅ **Autonomous Agent** - Not scripted responses; uses Google Gemma 4 31B with tool calling via OpenRouter
- ✅ **Production-Ready** - Deployed on Render.com with rate limiting, CORS, health checks
- ✅ **Tool Calling** - Captures leads, sends emails, records unknown questions
- ✅ **Guardrails** - Stays on-topic, enforces first-person identity, handles scope violations
- ✅ **Multi-Provider Email** - Fallback system: Resend → SendGrid → SMTP
- ✅ **Context-Aware** - Loads bio from structured text files, maintains conversation state

---

## ✨ Key Features

### 🧠 Intelligent Agent Core
- **Google Gemma 4 31B** via OpenRouter using OpenAI SDK compatibility layer
- **Context loading** from structured text files (`summary.txt`, `linkedin.txt`, `portfolio.txt`)
- **First-person identity enforcement** - Agent speaks as "I", never third-person
- **Language detection** - Responds in English or Finnish based on user input
- **Conversation state** - Maintains context across multi-turn dialogues

### 🛠️ Tool Calling System
```python
Tools:
├── record_user_details()    # Captures email, name, notes when user provides contact
├── record_unknown_question() # Logs questions agent can't answer
└── send_email()             # Multi-provider email orchestration
```

### 🔐 Security & Production Features
- **Rate Limiting**: 5 requests/minute, 50 requests/day per IP (SlowAPI)
- **CORS**: Configured for Vercel deployments + custom domain
- **Health Checks**: `/health` endpoint for monitoring services
- **Timeout Protection**: 30-second LLM timeout prevents hanging
- **Environment-based Config**: All secrets in env vars, not code

### 📧 Email Orchestration
Multi-provider fallback system with automatic failover:
1. **Resend API** (primary, production-recommended)
2. **SendGrid API** (secondary)
3. **Gmail SMTP** (local development fallback)

Automatically sends notifications for:
- New portfolio leads (with contact details)
- Unknown questions (for knowledge base improvement)

### 🛡️ Guardrails & Scope Management
- **On-topic enforcement** - Redirects off-topic questions back to portfolio/work
- **No general tech support** - Won't debug user code or teach programming
- **Professional tone** - Confident but not salesy, technical but approachable
- **Work request detection** - Suggests email for project inquiries, stays conversational for simple questions

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                      │
│                  https://samirautanen.fi                    │
└────────────────────────┬────────────────────────────────────┘
                         │ POST /chat
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend (api.py)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Rate Limiter │  │     CORS     │  │    Health    │     │
│  │  (SlowAPI)   │  │  Middleware  │  │    Check     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Agent Logic (agent_logic.py)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Me() Agent Class                                    │  │
│  │  ├─ Context Loading (me/*.txt)                       │  │
│  │  ├─ System Prompt (identity, guardrails, examples)   │  │
│  │  └─ Conversation Loop (tool calling support)         │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
┌──────────────────────┐    ┌──────────────────────┐
│  OpenRouter (Gemma)  │    │   Email System       │
│  (via OpenAI SDK)    │    │  ┌────────────────┐  │
│                      │    │  │ Resend API     │  │
│  - Tool calling      │    │  ├────────────────┤  │
│  - Context window    │    │  │ SendGrid API   │  │
│  - Streaming         │    │  ├────────────────┤  │
└──────────────────────┘    │  │ Gmail SMTP     │  │
                            │  └────────────────┘  │
                            └──────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | FastAPI + Uvicorn |
| **AI Model** | Google Gemma 4 31B (OpenRouter) |
| **SDK** | OpenAI Python SDK (compatibility mode) |
| **Rate Limiting** | SlowAPI |
| **Email** | Resend / SendGrid / SMTP |
| **Deployment** | Render.com |
| **Environment** | Python 3.10+ |

---

## 📡 API Endpoints

### `GET /`
Root endpoint, returns agent status.

**Response:**
```json
{
  "status": "ok",
  "agent": "Sami Rautanen AI Clone"
}
```

### `GET /health`
Health check for monitoring services (UptimeRobot, etc.).

**Response:**
```json
{
  "status": "healthy"
}
```

### `POST /chat`
Main chat endpoint. Accepts user message + conversation history.

**Rate Limits:**
- 5 requests/minute per IP
- 50 requests/day per IP

**Request:**
```json
{
  "message": "What's your experience with AI agents?",
  "history": [
    {"role": "user", "content": "Hi!"},
    {"role": "assistant", "content": "Hello! I'm Sami. Ask me anything about my work."}
  ]
}
```

**Response:**
```json
{
  "reply": "I've built several multi-agent systems, including a 6-agent Sales Intelligence Team and a 3-agent Deep Research Team. I specialize in agentic AI orchestration with tool calling and memory management."
}
```

**Error Responses:**
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Agent initialization failed or LLM timeout

---

## 🤖 Agent Capabilities

### Context-Aware Responses
The agent loads context from three text files:
- `me/summary.txt` - Professional summary and background
- `me/linkedin.txt` - LinkedIn profile content
- `me/portfolio.txt` - Portfolio projects and skills

This context is injected into every conversation, allowing the agent to answer detailed questions about my work, experience, and availability.

### Tool Calling
The agent can autonomously decide to use tools based on conversation context:

**`record_user_details(email, name, notes)`**
- Triggered when user provides contact information
- Sends email notification with lead details
- Captures context about their inquiry

**`record_unknown_question(question)`**
- Triggered when agent doesn't know the answer
- Logs question for knowledge base improvement
- Sends notification for manual follow-up

### Guardrails
Sophisticated prompt engineering ensures the agent:
- ✅ Always speaks in first-person ("I", "my", never "Sami", "his")
- ✅ Stays on-topic (portfolio, work, skills)
- ✅ Redirects off-topic questions professionally
- ✅ Suggests email for real project inquiries
- ✅ Doesn't provide general tech support or debugging
- ✅ Maintains professional but approachable tone

---

## 🚀 Deployment

### Local Development

1. **Clone and install dependencies:**
```bash
git clone https://github.com/Samrude1/ai-agent-backend.git
cd ai-agent-backend
pip install -r requirements.txt
```

2. **Set up environment variables:**
Create `.env` file:
```bash
OPENROUTER_API_KEY=your_openrouter_api_key
RECIPIENT_EMAIL=your_email@example.com

# Email provider (choose one):
RESEND_API_KEY=your_resend_key          # Recommended for production
# OR
SENDGRID_API_KEY=your_sendgrid_key
SENDGRID_VERIFIED_SENDER=verified@example.com
# OR
SMTP_EMAIL=your_gmail@gmail.com
SMTP_PASSWORD=your_app_password
```

3. **Run locally:**
```bash
uvicorn api:app --reload
```

Server runs on `http://localhost:8000`

### Production Deployment (Render.com)

See [DEPLOY_AGENT.md](DEPLOY_AGENT.md) for detailed deployment instructions.

**Quick setup:**
1. Connect GitHub repo to Render
2. Set root directory: `ai-agent-backend`
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn api:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in Render dashboard

**Cold Start Handling:**
- Render free tier sleeps after 15 minutes
- Frontend has retry logic with health checks
- See [COLD_START_SOLUTION.md](COLD_START_SOLUTION.md) for details
- Optional: Use UptimeRobot to keep backend awake ([KEEP_ALIVE.md](KEEP_ALIVE.md))

---

## 📁 Project Structure

```
ai-agent-backend/
├── api.py                      # FastAPI app, endpoints, CORS, rate limiting
├── agent_logic.py              # Agent class, tools, system prompt
├── requirements.txt            # Python dependencies
├── me/                         # Context files for agent
│   ├── summary.txt            # Professional summary
│   ├── linkedin.txt           # LinkedIn profile
│   └── portfolio.txt          # Portfolio projects
├── .env                        # Environment variables (not in git)
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── DEPLOY_AGENT.md            # Deployment guide
├── COLD_START_SOLUTION.md     # Cold start handling docs
├── KEEP_ALIVE.md              # UptimeRobot setup guide
└── EMAIL_SETUP.md             # Email configuration guide
```

---

## 🧪 Testing

### Test Health Endpoint
```bash
curl http://localhost:8000/health
```

### Test Chat Endpoint
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What technologies do you work with?",
    "history": []
  }'
```

### Test Rate Limiting
Send 6 requests within a minute to trigger rate limit:
```bash
for i in {1..6}; do
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "test", "history": []}';
done
```

### Test Tool Calling
Provide an email address to trigger `record_user_details` tool:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My email is test@example.com, I want to discuss a project",
    "history": []
  }'
```

Check your `RECIPIENT_EMAIL` inbox for the notification.

---

## 🔐 Security Features

### Rate Limiting
- **Short-term**: 5 requests/minute per IP
- **Long-term**: 50 requests/day per IP
- Prevents API abuse and controls costs
- Uses SlowAPI with IP-based tracking

### CORS Configuration
Allows requests from:
- `https://*.vercel.app` (all Vercel preview deployments)
- `https://samirautanen.fi`
- `https://www.samirautanen.fi`
- `http://localhost:3000` (local development)

### Environment Variables
All sensitive data in environment variables:
- API keys (Gemini, Resend, SendGrid)
- Email credentials
- Recipient addresses
- Never committed to git

### Timeout Protection
- 30-second timeout on LLM calls
- Prevents hanging requests on Render
- Graceful error handling

---

## 📚 Documentation

- **[DEPLOY_AGENT.md](DEPLOY_AGENT.md)** - Complete deployment guide for Render.com
- **[COLD_START_SOLUTION.md](COLD_START_SOLUTION.md)** - Handling Render free tier cold starts
- **[KEEP_ALIVE.md](KEEP_ALIVE.md)** - UptimeRobot setup to prevent cold starts
- **[EMAIL_SETUP.md](EMAIL_SETUP.md)** - Email provider configuration guide

---

## 🎯 Future Enhancements

- [ ] Add conversation memory persistence (database)
- [ ] Implement streaming responses for better UX
- [ ] Add analytics dashboard for conversation insights
- [ ] Support for more languages (Swedish, German)
- [ ] Integration with calendar for meeting scheduling
- [ ] RAG system for dynamic portfolio updates
- [ ] Multi-agent orchestration (research agent, code reviewer)

---

## 📄 License

This repository is part of my portfolio to demonstrate technical capabilities. The code is public for transparency, but:
- ✅ Feel free to learn from the architecture and implementation
- ❌ Please don't deploy this as your own portfolio agent
- 💬 For collaboration or business inquiries: samrude1@outlook.com

---

## 🤝 Connect

- **Portfolio**: [samirautanen.fi](https://samirautanen.fi)
- **GitHub**: [@Samrude1](https://github.com/Samrude1)
- **LinkedIn**: [Sami Rautanen](https://linkedin.com/in/sami-rautanen)
- **Email**: samrude1@outlook.com

---

**Built with ❤️ and agentic AI** | Deployed live on [samirautanen.fi](https://samirautanen.fi)
