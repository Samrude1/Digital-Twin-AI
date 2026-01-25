# Autonomous Career Digital Twin (Backend)

> **Production-Grade Agentic Backend.** The autonomous intelligence engine powering the portfolio's Digital Twin, capable of handling professional inquiries, context-based reasoning, and email orchestration.

## 🏗️ System Architecture

This system is not a simple chatbot; it is a **deployed autonomous agent** built with FastAPI and Google Gemini 2.0 Flash.

*   **Core Engine:** Python 3.10+ / FastAPI
*   **Intelligence:** Google Gemini 2.0 Flash (via OpenAI Agents SDK patterns)
*   **Infrastructure:** Render.com (Production Cloud Deployment)
*   **Email Orchestration:** SMTP Integration for real-time notifications

## 🤖 Capabilities

1.  **Context-Aware Dialog:** Maintains conversation state to answer complex questions about my engineering background, tech stack, and availability.
2.  **Autonomous Email Workflow:**
    *   Detects high-value inquiries.
    *   Drafts, formats, and sends notifications to my personal inbox.
    *   Confirms receipt to the sender with professional automated responses.
3.  **Resilience & Security:**
    *   Rate-limiting middleware (SlowAPI)
    *   Environment-based configuration management
    *   Automated uptime monitoring

## 🚀 Deployment

The system is containerized and deployed on Render.com, handling live traffic from the frontend portfolio.

```bash
# Local Development
uvicorn api:app --reload

# Production Entrypoint
uvicorn api:app --host 0.0.0.0 --port $PORT
```

## 🔐 Security Note

This repository contains the backend logic. Sensitive keys (API tokens, SMTP credentials) are managed via encrypted environment variables in the deployment runtime.
