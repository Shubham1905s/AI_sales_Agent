# LeadGen AI — 100% Claude Powered

Full-stack B2B lead generation platform. **No mock data. No third-party lead databases.**
Everything — lead discovery, enrichment, scoring, and outreach — runs through the Claude API
with live web search.

## Stack
- **Frontend**: React 18 + Vite + TanStack Query
- **Backend**: FastAPI
- **Storage**: Local JSON file (`backend/data/leads.json`)
- **AI**: Claude Sonnet 4 (`claude-sonnet-4-20250514`) with `web_search` tool

## What Claude Does

| Action | How Claude Powers It |
|--------|----------------------|
| **Discover leads** | Searches the web for real companies + decision makers matching your natural language brief |
| **Enrich leads** | Web-searches company news, hiring signals, funding, tech stack, person context |
| **Score leads** | Evaluates ICP fit, intent signals, buying stage — returns 0–100 composite score |
| **Generate outreach** | Finds a real current hook (recent news/post/hiring), then writes LinkedIn + 3-step email |

## Quick Start

### 1. Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env — add ANTHROPIC_API_KEY
uvicorn app.main:app --reload
```

Backend: http://localhost:8000  
API docs: http://localhost:8000/docs

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## .env
```
ANTHROPIC_API_KEY=sk-ant-...
DATA_FILE=data/leads.json
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/leads/ | List all leads with scores |
| POST | /api/leads/ | Add a lead manually (Claude enriches + scores automatically) |
| POST | /api/leads/discover | **Claude discovers real leads from a natural language brief** |
| GET | /api/leads/{id} | Get full lead detail |
| POST | /api/leads/{id}/score | Re-score with Claude |
| POST | /api/leads/{id}/enrich | Re-enrich with Claude web search |
| POST | /api/leads/{id}/outreach | Generate LinkedIn + 3-step email outreach |
| DELETE | /api/leads/{id} | Delete a lead |

## Discover API Example
```json
POST /api/leads/discover
{
  "target": "Automotive ADAS companies in Germany with VP or Director level R&D decision makers",
  "max_leads": 10,
  "auto_enrich": true,
  "auto_score": true
}
```
Claude searches the web, finds matching companies and people, enriches each record,
and scores every lead — all in one call.
