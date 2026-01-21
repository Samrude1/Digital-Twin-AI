# AI Chatbot Email Setup - Quick Guide

## ✅ What Was Added

Email functionality so you receive client details when AI chatbot collects contact information.

**Features:**
- 📧 Email notifications with client name, email, notes
- ⏰ Timestamp of inquiry
- 📱 Optional Pushover mobile notifications (if configured)
- ❓ Unknown question alerts

---

## 🔧 Configuration Required

You need to set these environment variables on your Render backend:

### Required for Email:
1. **SMTP_EMAIL** - Your Gmail address (e.g., `yourname@gmail.com`)
2. **SMTP_PASSWORD** - Gmail App Password (NOT your regular password!)
3. **RECIPIENT_EMAIL** - Where you receive notifications (e.g., `samrude1@outlook.com`)

### Optional (for mobile push):
4. **PUSHOVER_USER** - Pushover user key
5. **PUSHOVER_TOKEN** - Pushover API token

---

## 📧 How to Get Gmail App Password

**Step 1:** Enable 2-Factor Authentication on Gmail
1. Go to https://myaccount.google.com/security
2. Turn on "2-Step Verification" if not already enabled

**Step 2:** Create App Password
1. Go to https://myaccount.google.com/apppasswords
2. Sign in to your Gmail
3. Select "Mail" as the app
4. Select "Other" as the device, name it "Portfolio AI"
5. Click "Generate"
6. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

**Step 3:** Add to Render
1. Go to Render Dashboard → Your Service → Environment
2. Add:
   - Key: `SMTP_EMAIL` → Value: `yourname@gmail.com`
   - Key: `SMTP_PASSWORD` → Value: `abcd efgh ijkl mnop` (app password)
   - Key: `RECIPIENT_EMAIL` → Value: `samrude1@outlook.com`

---

## 🧪 Testing

**Local Testing:**

1. Create `.env` file in `ai-agent-backend` folder:
```
GEMINI_API_KEY=your_gemini_key
SMTP_EMAIL=yourname@gmail.com
SMTP_PASSWORD=your_app_password
RECIPIENT_EMAIL=samrude1@outlook.com
```

2. Run backend locally:
```bash
cd ai-agent-backend
uvicorn api:app --reload
```

3. Test chatbot and give it your test email
4. Check if you receive an email!

**Production Testing:**
1. Deploy to Render with environment variables set
2. Visit your portfolio site
3. Chat with AI and provide test contact info
4. Check your email inbox

---

## 📨 Email Format

When someone provides contact info, you'll receive:

**Subject:** 🎯 New Portfolio Lead: [Name]

**Body:**
```
New contact from portfolio AI chatbot:

Name: John Doe
Email: john@example.com
Notes: Interested in building a web app

Time: 2026-01-21 13:30:00
```

---

## 🔍 Troubleshooting

**"Email not configured" in logs:**
- Check environment variables are set correctly on Render
- Verify SMTP_EMAIL, SMTP_PASSWORD, RECIPIENT_EMAIL all exist

**"Failed to send email: authentication failed":**
- You're using regular Gmail password instead of App Password
- Generate new App Password and update SMTP_PASSWORD

**"Failed to send email: connection refused":**
- Gmail might be blocking the connection
- Check if 2-Factor Auth is enabled
- Try generating new App Password

**Not receiving emails:**
- Check spam/junk folder
- Verify RECIPIENT_EMAIL is correct
- Check Render logs for errors

---

## 🚀 Deployment

1. **Add environment variables to Render:**
   - SMTP_EMAIL
   - SMTP_PASSWORD  
   - RECIPIENT_EMAIL

2. **Commit and push code:**
```bash
cd ai-agent-backend
git add agent_logic.py DEPLOY_AGENT.md
git commit -m "Add email notifications for client inquiries"
git push origin master
```

3. **Render auto-deploys** - check logs for "Email sent successfully"

---

## ✨ Next Steps

Optional enhancements:
- Add Pushover for mobile notifications
- Customize email template
- Add auto-reply to clients
- Log all inquiries to database

**Current setup:** Email only (simple and reliable!)
