# Deploying Your AI Agent API

You have two parts:
1.  **Backend (Python/FastAPI):** Must be hosted on a server (e.g., Render, Railway).
2.  **Frontend (React/Next.js):** Hosted on Vercel (already done).

## Step 1: Deploy Backend to Render.com

1.  **Push to GitHub:**
    Make sure this folder `ai-agent-backend` is in your GitHub repo.
    (If it's inside a monorepo, you might need to specify the "Root Directory" in Render).

2.  **Create New Web Service on Render:**
    *   **Connect GitHub:** Select your repository.
    *   **Name:** `sami-ai-agent` (or similar).
    *   **Root Directory:** `ai-agent-backend` (Important! Since the code is in a subfolder).
    *   **Runtime:** Python 3.
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `uvicorn api:app --host 0.0.0.0 --port $PORT`

3.  **Environment Variables:**
    In Render Dashboard -> Environment, add:
    *   `GEMINI_API_KEY`: [Your Google Gemini API Key]
    *   `PUSHOVER_USER`: [Optional, for notifications]
    *   `PUSHOVER_TOKEN`: [Optional]

4.  **Get URL:**
    Render will give you a URL like `https://sami-ai-agent.onrender.com`.

## Step 2: Connect Frontend

1.  Open your local project.
2.  Open `.env.local` (create it if missing) in `portfolio-2026/`.
3.  Add:
    ```
    NEXT_PUBLIC_API_URL=https://sami-ai-agent.onrender.com
    ```
4.  Redeploy Vercel (`npx vercel`).

## Local Testing

1.  **Start Backend:**
    ```bash
    cd ai-agent-backend
    pip install -r requirements.txt
    uvicorn api:app --reload
    ```
    (Runs on `http://localhost:8000`)

2.  **Start Frontend:**
    ```bash
    cd portfolio-2026
    npm run dev
    ```
    (The chat widget defaults to localhost:8000 if no env var is set).
