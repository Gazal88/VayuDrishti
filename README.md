# VayuDrishti

**Live demo → https://vayu-drishti-ys2l.vercel.app/**

Air quality intelligence for Indian cities — personalised exposure scores, real-time AQI, and AI-generated health advisories.

Live weather and pollution data from [Open-Meteo](https://open-meteo.com) (free, no API key required). AI advisories powered by Google Gemini.

---

## What it does

Search any Indian city and get:

- Real-time AQI, PM2.5, temperature, humidity, and wind
- A personalised exposure score based on your age, health condition, and occupation
- The best time window to go outside today (lowest exposure)
- A plain-English AI advisory explaining your specific risk

The same AQI reads differently for an asthmatic outdoor worker versus a healthy desk employee. VayuDrishti shows that difference.

---

## Stack

**Frontend** — React 18, Vite, Framer Motion, Three.js (weather particle overlays)

**Backend** — FastAPI, Python 3.13, httpx, Pydantic v2

**Data** — Open-Meteo weather API, Open-Meteo air quality API, Open-Meteo geocoding

**AI** — Google Gemini 3.6 Flash (or Groq Llama as fallback)

---

## Running locally

**Backend**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r ../requirements.txt
python run.py
```

Server starts at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

**Frontend**

```bash
npm install
npm run dev
```

Frontend at `http://localhost:5173`. API calls are proxied to the backend automatically.

---

## Environment variables

Copy `backend/.env.example` to `backend/.env` and fill in your keys.

```
GEMINI_API_KEY=your_key_here     # from https://aistudio.google.com/apikey
LLM_PROVIDER=gemini              # or groq
GROQ_API_KEY=                    # optional, faster alternative
```

Open-Meteo requires no API key.

---

## Deployment

**Frontend → Vercel**

Set `VITE_API_URL` in Vercel environment variables to your backend URL.

**Backend → Railway**

Set root to `/backend`, start command `python run.py`. Add all `.env` variables in Railway's environment settings.

---

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/dashboard?city=Delhi` | Live weather + AQI |
| GET | `/hourly-forecast?city=Delhi` | 24h hourly data |
| POST | `/exposure-score` | Personalised risk score |
| POST | `/advisory` | AI health advisory |
| POST | `/analyze` | All of the above in one call |

---

## Exposure score formula

```
score = (base_aqi_risk + heat_bonus + pm25_bonus)
        × condition_multiplier
        × occupation_multiplier
        × age_multiplier
```

Score range 0–10. Fully deterministic — the AI explains the number, never invents it.


