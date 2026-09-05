# VayuDrishti — Backend

FastAPI + Open-Meteo + Gemini (or Groq). No paid weather API needed.

---

## Setup

```bash
cd backend

# 1. Create and activate virtualenv
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
#    .env is already present — just fill in your API key if missing:
#    GEMINI_API_KEY=your_key_here
#    LLM_PROVIDER=gemini

# 4. Start the server
python run.py
# or: uvicorn app.main:app --reload --port 8000
```

Server runs at: **http://localhost:8000**
Interactive docs: **http://localhost:8000/docs**

---

## Endpoints

| Method | Path               | Description                              |
|--------|--------------------|------------------------------------------|
| GET    | `/dashboard`       | Live weather + AQI for a city            |
| GET    | `/hourly-forecast` | 24h hourly AQI + temperature             |
| POST   | `/exposure-score`  | Personalised exposure score + best window|
| POST   | `/advisory`        | AI advisory text (Gemini / Groq)         |
| POST   | `/analyze`         | One-shot: all of the above combined      |
| GET    | `/health`          | Health check                             |

---

## Frontend connection

The React frontend (Vite, port 5173) proxies `/api/*` → `http://localhost:8000/*`.

In `src/hooks/useApi.js` set:

```js
export const USE_DUMMY = false   // ← already set; keep false for live data
```

Both services must be running simultaneously:

```bash
# Terminal 1 — backend
cd backend && python run.py

# Terminal 2 — frontend
npm run dev
```

---

## LLM Provider

Configured via `.env`:

```
LLM_PROVIDER=gemini          # gemini | groq | auto
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key        # optional, fast alternative
```

`auto` prefers Groq if both keys are set (faster), falls back to Gemini.

---

## Profile Enums (must match frontend)

**AgeGroup:** `18-30` | `31-50` | `51-65` | `65+`

**HealthCondition:** `none` | `asthma` | `heart_condition` | `pregnant` | `other`

**Occupation:** `desk_job` | `outdoor_worker` | `student` | `elderly_caregiver`
