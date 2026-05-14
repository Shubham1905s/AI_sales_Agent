# LeadGen AI — Running Steps

## What's Inside This ZIP

```
leadgen/
├── RUNNING_STEPS.md          ← You are here
├── README.md                 ← Project overview
├── setup.sh                  ← Auto setup script (Mac/Linux)
│
├── backend/                  ← Python FastAPI server
│   ├── .env.example          ← Copy this to .env and fill keys
│   ├── data/
│   │   └── leads.json        ← Local JSON store for leads, scores, outreach
│   ├── requirements.txt      ← Python dependencies
│   └── app/
│       ├── main.py           ← FastAPI app entry point
│       ├── core/
│       │   ├── config.py     ← Reads .env settings
│       │   └── json_store.py ← JSON file read/write helpers
│       ├── models/
│       │   └── models.py     ← Lead status enum
│       ├── api/
│       │   └── leads.py      ← All 7 API routes
│       └── services/
│           └── claude_service.py  ← Claude AI: scoring, outreach, enrichment
│
└── frontend/                 ← React + Vite app
    ├── index.html
    ├── package.json          ← Node dependencies
    ├── vite.config.js        ← Dev server + API proxy
    └── src/
        ├── App.jsx           ← Router setup
        ├── main.jsx          ← React entry point
        ├── index.css         ← Global dark theme styles
        ├── lib/
        │   └── api.js        ← Axios API client
        └── pages/
            ├── Dashboard.jsx ← Lead list, stats, add form
            └── LeadDetail.jsx← Score, outreach, enrichment tabs
```

---

## Prerequisites — Install These First

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.11+ | https://python.org |
| Node.js | 20+ LTS | https://nodejs.org |
| Git (optional) | any | https://git-scm.com |

---

## Step 1 — Get Your Anthropic API Key

1. Go to https://console.anthropic.com
2. Sign up / Log in
3. Click **API Keys** → **Create Key**
4. Copy the key (starts with `sk-ant-...`)
5. Keep it safe — you'll need it in Step 3

---

## Step 2 — Setup Backend

```bash
# Go into backend folder
cd leadgen/backend

# Create Python virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate        # Mac/Linux
# OR
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Create your .env file
cp .env.example .env
```

Now open `.env` in any text editor and fill in:

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
DATA_FILE=data/leads.json
APP_ENV=development
```

---

## Step 3 — Start the Backend Server

```bash
# Make sure you're in backend/ with venv activated
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

✅ Backend is running! Test it: http://localhost:8000/health → should return `{"status":"ok"}`

API docs available at: http://localhost:8000/docs

---

## Step 4 — Setup & Start Frontend

Open a **new terminal** (keep backend running):

```bash
# Go into frontend folder
cd leadgen/frontend

# Install Node dependencies
npm install

# Start dev server
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms
  ➜  Local:   http://localhost:5173/
```

✅ Frontend is running!

---

## Step 5 — Open the App

Go to: **http://localhost:5173**

You'll see the LeadGen AI dashboard. Now you can:

1. **Add Lead** → Click "Add Lead" button → fill in name, title, company
2. **Score with AI** → Click on any lead → "Score with AI" → Claude scores 0-100
3. **Enrich with Web** → Claude searches the web for company info
4. **Generate Outreach** → Claude writes LinkedIn DM + 3 email sequence

---

## API Endpoints (for reference)

| Method | URL | What it does |
|--------|-----|-------------|
| GET | /api/leads/ | List all leads |
| POST | /api/leads/ | Create a lead |
| GET | /api/leads/{id} | Get one lead with score + outreach |
| DELETE | /api/leads/{id} | Delete a lead |
| POST | /api/leads/{id}/score | AI score the lead |
| POST | /api/leads/{id}/enrich | Enrich with web search |
| POST | /api/leads/{id}/outreach | Generate LinkedIn + email outreach |

---

## Common Issues & Fixes

**"ModuleNotFoundError: No module named 'app'"**
→ Make sure you're running `uvicorn` from inside the `backend/` folder

**"Invalid API Key" from Claude**
→ Check your `.env` file — ANTHROPIC_API_KEY must start with `sk-ant-`

**Frontend shows blank / network error**
→ Make sure backend is running on port 8000 before starting frontend

---

## Stopping the Servers

- Press `Ctrl + C` in each terminal to stop backend and frontend
- Deactivate Python venv: `deactivate`
