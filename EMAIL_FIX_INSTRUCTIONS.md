# Fixing Email on Render (Action Required)

## The Problem
Render (and most cloud platforms) **completely blocks** the standard email ports (25, 465, 587) to prevent spam. This is a platform-level firewall that code cannot bypass. That is why you see `[Errno 101] Network is unreachable` despite the code being correct for local use.

## The Solution: Switch to API
I have updated the backend to support **Resend**, a modern email API that sends emails via HTTP (web requests) instead of SMTP. This bypasses the port block completely and is the standard way to send email from Render.

### Option A: Resend (Easiest)
1. Go to [Resend.com](https://resend.com) and sign up (free).
2. Get your API Key.
3. Add `RESEND_API_KEY` to Render Environment.

### Option B: SendGrid (If you already have it)
1. Get your API Key from SendGrid.
2. Ensure you have a **verified sender identity** in SendGrid that matches your `SMTP_EMAIL` (or just use your verified email).
3. Add `SENDGRID_API_KEY` to Render Environment.
4. Note: SendGrid APIs require the "From" address to be a verified sender in your SendGrid dashboard.

### 4. Save and Redeploy
1. Go to your [Render Dashboard](https://dashboard.render.com/).
2. Click on your `ai-agent-backend` service.
3. Go to **Environment**.
4. Add a new variable:
   - **Key:** `RESEND_API_KEY`
   - **Value:** `re_123456789...` (Paste your key)

### 4. Save and Redeploy
Render will likely auto-deploy when you save.

Once this key is present, the chatbot will automatically detect it and use the API method instead of the blocked SMTP method.
