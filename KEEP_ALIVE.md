# Keep Backend Awake (Render Free Tier)

Render's free tier puts your service to sleep after **15 minutes of inactivity**. This causes a **30-60 second cold start** when someone visits your site.

## Solution: Free Cron Job Services

Use a free service to ping your backend every 5-10 minutes to keep it awake.

### Option 1: UptimeRobot (Recommended)
**Free tier: 50 monitors, 5-minute intervals**

1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Sign up for free account
3. Create new monitor:
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** Sami AI Agent
   - **URL:** `https://sami-ai-agent.onrender.com/health`
   - **Monitoring Interval:** 5 minutes
4. Done! Your backend will stay awake 24/7

### Option 2: Cron-Job.org
**Free tier: Unlimited jobs, 1-minute minimum interval**

1. Go to [cron-job.org](https://cron-job.org)
2. Sign up for free account
3. Create new cron job:
   - **Title:** Keep Sami AI Awake
   - **URL:** `https://sami-ai-agent.onrender.com/health`
   - **Schedule:** Every 10 minutes
4. Save and enable

### Option 3: BetterUptime (formerly Uptime Robot alternative)
**Free tier: 10 monitors, 3-minute intervals**

1. Go to [betteruptime.com](https://betteruptime.com)
2. Sign up for free account
3. Create monitor with your `/health` endpoint

## Cost Consideration

**Render Free Tier Limits:**
- 750 hours/month (enough for 24/7 if you have only one service)
- Sleeps after 15 min inactivity
- Cold start: ~30-60 seconds

**If you keep it awake 24/7:**
- ✅ No cold starts
- ✅ Better user experience
- ⚠️ Uses all 750 hours (but that's what they're for!)

## Alternative: Accept Cold Starts

If you prefer to save resources, the frontend now handles cold starts gracefully:
- ✅ Health check before first message
- ✅ Automatic retry with exponential backoff
- ✅ User-friendly status messages
- ✅ Shows "Waking up backend... (~30-60s)" message

**This is already implemented in `ChatWidget.tsx`!**

## Recommendation

**For portfolio/demo sites:** Use UptimeRobot to keep it awake. Recruiters won't wait 60 seconds.

**For low-traffic projects:** Let it sleep and rely on the frontend's retry logic.
