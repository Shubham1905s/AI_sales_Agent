# ⚡ Quick Start: Dynamic Lead Generation

Get your AI Sales Agent running with Claude-powered lead discovery in **3 steps**.

---

## Step 1: Set Up Environment

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configure API Key
Edit `backend/.env`:
```
ANTHROPIC_API_KEY=sk-ant-YOUR_API_KEY_HERE
DATA_FILE=data/leads.json
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

Get your API key: https://console.anthropic.com/account/keys

### Frontend Setup
```bash
cd frontend
npm install
```

---

## Step 2: Start Services

### Terminal 1: Backend API
```bash
cd backend
venv\Scripts\activate  # Activate venv if not already
python -m uvicorn app.main:app --reload
```

Expected output:
```
INFO:     Started server process [1234]
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Terminal 2: Frontend Dev Server
```bash
cd frontend
npm run dev
```

Expected output:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

---

## Step 3: Test Lead Discovery

### 1. Open Frontend
Go to: http://localhost:5173

You should see:
- Dashboard with KPI cards
- Discover button in top right

### 2. Click "Discover" Tab

### 3. Enter Your Target
Paste this example:
```
B2B SaaS companies in India (Bangalore, Pune) with 50-500 employees, 
seed to Series A stage, using Python/Node.js/Go stack, VP Engineering or CTO.
```

### 4. Configure Options
- ✓ Auto-enrich: ON (recommended)
- ✓ Auto-score: ON (recommended)
- Find up to: 10 leads

### 5. Click "Discover with Claude"

Wait 30-90 seconds. You'll see:
- Loading message: "Claude is searching…"
- After completion: Found X new leads

### 6. View Results
- Click "Leads" tab to see all discovered leads
- Click any lead to see full details:
  - Company intelligence (size, funding, tech stack)
  - Buying signals and pain points
  - Lead score (0-100)
  - Recommended next action
  - Generated outreach messages

---

## What Just Happened

1. **Discovery** - Claude used web search to find companies + decision makers
2. **Enrichment** - Claude researched each company:
   - Industry, size, funding stage
   - Technology stack
   - Recent news and hiring signals
   - Pain points and growth stage
3. **Scoring** - Claude evaluated:
   - ICP fit (company match)
   - Lead authority (title/decision-making power)
   - Buying intent (signals + news)
   - Overall priority (hot/warm/cold)
4. **Outreach** - Claude generated:
   - LinkedIn connection message
   - 3-email sequence

All data is **real, web-verified**, no mock data.

---

## Next Actions

### ✅ Try It Out
- [ ] Modify search criteria and run again
- [ ] Try different industries/regions
- [ ] Add a lead manually (Add Lead tab)
- [ ] Click a lead to view full enrichment
- [ ] Generate outreach for a hot lead

### 📚 Learn More
See [DYNAMIC_LEAD_GENERATION.md](./DYNAMIC_LEAD_GENERATION.md) for:
- Full feature guide
- API endpoints documentation
- Best practices for search queries
- Troubleshooting

### 🚀 Advanced Setup
- **Database**: Currently uses JSON. Upgrade to PostgreSQL for production.
- **Caching**: Add Redis to cache enrichment data.
- **Scheduling**: Build background job to run discovery on schedule.
- **Export**: Add CSV/Excel export for leads.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key is missing" | Check `backend/.env` has valid `ANTHROPIC_API_KEY` |
| "Port 8000 already in use" | Change to `python -m uvicorn app.main:app --reload --port 8001` |
| "Port 5173 already in use" | Change to `npm run dev -- --port 5174` |
| "Claude is searching…" takes >2 min | Normal for 20+ leads. Internet connection OK? |
| Leads not saving | Check `data/` folder exists and has write permissions |
| Blank enrichment data | Claude couldn't find public info. Try adding more lead details manually. |

---

## API Quick Reference

| Action | Command |
|--------|---------|
| **Discover leads** | `curl -X POST http://localhost:8000/api/leads/discover -H "Content-Type: application/json" -d '{"target":"DevOps engineers at 1000+ companies","max_leads":10,"auto_enrich":true,"auto_score":true}'` |
| **Add lead manually** | `curl -X POST http://localhost:8000/api/leads -H "Content-Type: application/json" -d '{"first_name":"John","last_name":"Doe","company":"Google","title":"Engineer"}'` |
| **List all leads** | `curl http://localhost:8000/api/leads` |
| **Get lead details** | `curl http://localhost:8000/api/leads/{lead_id}` |
| **Score a lead** | `curl -X POST http://localhost:8000/api/leads/{lead_id}/score` |
| **Enrich a lead** | `curl -X POST http://localhost:8000/api/leads/{lead_id}/enrich` |
| **Generate outreach** | `curl -X POST http://localhost:8000/api/leads/{lead_id}/outreach` |

Replace `{lead_id}` with actual UUID from `/api/leads`.

---

## Key Takeaways

✅ **Dynamic** - Leads generated on-demand, no hardcoding
✅ **AI-Powered** - 100% Claude AI with real web search
✅ **Real Data** - All info verified via web, no mock data
✅ **Enriched** - Company intelligence + buying signals
✅ **Scored** - ICP fit + intent + authority evaluation
✅ **Actionable** - Personalized outreach sequences ready

---

**Ready to discover your next 10 sales-qualified leads?** Click the Discover tab and describe your ideal customer. Claude will handle the rest.
