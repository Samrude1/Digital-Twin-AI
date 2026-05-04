# Tarkista Miksi Backend Pysyy Hereillä

## 1. Tarkista Render Dashboard

### Events Log
1. Mene: https://dashboard.render.com
2. Valitse: `sami-ai-agent` (tai mikä nimesi on)
3. Klikkaa: **"Events"** välilehti
4. Katso: Näkyykö "Service sleeping" tai "Service waking up" viestejä?

**Jos EI näy "sleeping" viestejä → Backend ei ole koskaan nukkunut!**

### Metrics
1. Samassa dashboardissa: **"Metrics"** välilehti
2. Katso: **Request Rate** graafi
3. Näkyykö säännöllisiä requesteja?

**Jos näkyy requesteja joka 5-15 min → Joku pingaa sitä!**

### Logs
1. Klikkaa: **"Logs"** välilehti
2. Katso: Mitä requesteja tulee?
3. Etsi rivejä kuten:
   ```
   GET /health
   GET /
   HEAD /health
   ```

**Jos näkyy säännöllisiä GET/HEAD requesteja → Monitor on päällä!**

## 2. Tarkista Onko UptimeRobot/Muu Monitor Päällä

### UptimeRobot
1. Mene: https://uptimerobot.com/dashboard
2. Kirjaudu sisään (jos sinulla on tili)
3. Katso: Onko `sami-ai-agent` monitorissa?

### Cron-Job.org
1. Mene: https://cron-job.org
2. Kirjaudu sisään (jos sinulla on tili)
3. Katso: Onko cron job päällä?

### BetterUptime
1. Mene: https://betteruptime.com
2. Kirjaudu sisään (jos sinulla on tili)
3. Katso: Onko monitor päällä?

## 3. Tarkista Vercel Deployments

1. Mene: https://vercel.com/dashboard
2. Valitse: `portfolio-2026` projekti
3. Katso: **"Deployments"** välilehti
4. Onko vanhoja preview deployments auki?

**Preview deployments saattavat pingata backendiä!**

## 4. Testaa Manuaalisesti Cold Start

### Pakota Backend Nukkumaan
1. Mene Render dashboardiin
2. Valitse palvelu
3. Klikkaa: **"Manual Deploy"** → **"Suspend"**
4. Odota 2 minuuttia
5. Avaa: `https://sami-ai-agent.onrender.com/health`

**Jos lataa kauan → Backend oli nukkumassa ✅**
**Jos vastaa heti → Jotain pitää sen hereillä ❌**

## 5. Katso Render Plan Details

1. Render dashboardissa
2. Valitse palvelu
3. Katso: **"Settings"** → **"Plan"**
4. Onko: **"Free"** vai jotain muuta?

**Jos näkyy jotain muuta kuin "Free" → Sinulla saattaa olla maksullinen tier!**

## Tulokset

### Jos Backend Nukkuu Normaalisti
- ✅ Retry-logiikka on hyödyllinen
- ✅ Pidä muutokset
- ✅ Harkitse UptimeRobot myöhemmin

### Jos Backend Ei Koskaan Nuku
- ❓ Etsi mikä pitää sen hereillä (ks. yllä)
- ❓ Ehkä sinulla on jo monitor päällä?
- ❓ Tai Render on muuttanut käytäntöjään?
- ✅ Retry-logiikka ei haittaa, mutta ei ole välttämätön

## Yhteenveto

**Todennäköisin syy:** Sinulla on jo UptimeRobot tai vastaava monitor päällä, jonka olet unohtanut! 😄

Tarkista kaikki monitoring-palvelut joissa sinulla on tili.
