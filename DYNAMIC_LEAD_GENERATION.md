# Dynamic Lead Generation Guide

## Overview

Your AI Sales Agent now has **fully dynamic lead generation** powered by Claude AI. Instead of hardcoded leads, the system:

1. **Discovers leads** - Claude uses web search to find real companies and decision makers matching your criteria
2. **Enriches leads** - Automatically gathers company intelligence: industry, size, funding, tech stack, pain points, buying signals
3. **Scores leads** - Evaluates ICP fit, buying intent, and prioritizes outreach
4. **Generates outreach** - Creates personalized LinkedIn messages and email sequences

---

## How It Works (Architecture)

### Data Flow

```
User Input (Discover Tab)
    ↓
Claude Web Search (via Anthropic API)
    ↓
Leads discovered + optional auto-enrich + auto-score
    ↓
JSON Store (leads.json) - persisted
    ↓
Frontend displays results + allows manual enrich/score
```

### Backend Services

- **`claude_lead_finder.py`** - Uses Claude + web_search to find real leads
- **`claude_service.py`** - Enriches leads with company intelligence; scores leads; generates outreach
- **`anthropic_client.py`** - Handles Claude API calls with web search tool
- **`json_store.py`** - Thread-safe JSON persistence (reads/writes `leads.json`)
- **`leads.py`** - FastAPI routes for discovery, CRUD, enrichment, scoring, outreach

### Frontend Components

- **Discover Tab** - Input natural language target; auto-enrich/score toggles; results display
- **Add Lead Tab** - Manual entry with auto-analysis by Claude
- **Leads Table** - Browse all leads with scores, prioritize hot leads
- **Lead Detail** - View full enrichment data and generated outreach messages

---

## Usage Guide

### 1. Discovering Leads (Main Feature)

#### Step 1: Navigate to Discover Tab
Click the **Discover** button in the header.

#### Step 2: Describe Your Target
Write a natural language description of who you're looking for. Examples:

✓ **Good:**
- "Automotive ADAS companies in Germany and France with VP or Director level decision makers in R&D or data engineering, 500–20,000 employees"
- "AI infrastructure startups in US (Series A/B stage) with CTOs or VP Engineering"
- "Insurance companies in Japan with 100–500 employees that use cloud platforms"

✗ **Avoid:**
- "tech companies" (too broad)
- "anyone in sales" (not specific enough)
- Overly technical requirements (Claude handles that via web search)

#### Step 3: Configure Options
- **Find up to N leads**: Choose 5–25 (more leads = longer search)
- **Auto-enrich**: ✓ Recommended. Claude will research each lead's company intelligence
- **Auto-score**: ✓ Recommended. Claude will evaluate ICP fit and buying intent

#### Step 4: Click "Discover with Claude"
Wait 30–120 seconds. Claude will:
1. Search the web for companies matching your criteria
2. Find decision makers at each company
3. Gather company intelligence (if auto-enrich enabled)
4. Score leads (if auto-score enabled)
5. Save new leads to the database

#### Step 5: Review Results
- Newly discovered leads appear in the results panel
- Duplicates are skipped (by email or name + company)
- Navigate to **Leads** tab to view full details

---

### 2. Viewing & Managing Leads

#### Leads List
- **Score Ring**: Color-coded lead quality (green = hot 70+, amber = warm 45–69, gray = cold <45)
- **Status**: "new", "scored", "outreach_ready", "contacted"
- **Sort**: Most recent leads first

#### Lead Detail Page
Click any lead to view:
- **Full enrichment data**: Industry, company size, funding, tech stack, pain points, buying signals
- **Score breakdown**: Firmographic, title, intent, engagement scores + confidence level
- **Next best action**: Claude's recommendation for outreach
- **Reasoning**: Why this lead scored this way
- **Outreach messages**: Personalized LinkedIn message and email sequence

#### Actions
- **Score**: Re-score a lead or score a new one
- **Enrich**: Update enrichment data (useful if company situation changed)
- **Generate Outreach**: Create LinkedIn + email sequence for this lead
- **Delete**: Remove a lead from database

---

### 3. Adding Leads Manually

#### Step 1: Click "Add Lead" Button

#### Step 2: Fill in Known Information
Required:
- First name
- Last name

Optional (but helpful for better analysis):
- Email
- Title
- Company
- Company size
- Industry
- Location
- LinkedIn URL
- Website

#### Step 3: Click "Save & Analyse with Claude"
Claude will automatically:
1. Research the person + company via web search
2. Enrich with industry, funding, tech stack, pain points, buying signals
3. Score the lead (ICP fit, buying intent, urgency)
4. Suggest next best action

Result appears in **Leads** tab.

---

### 4. Enriching Leads

#### Automatic Enrichment
- Happens when you discover leads with **Auto-enrich** checked
- Happens when you add a manual lead

#### Manual Re-enrichment
1. Go to **Lead Detail**
2. Click **Enrich** button
3. Claude re-searches the web and updates:
   - Company intelligence (updated news, funding, hiring signals)
   - Technology stack
   - Pain points and buying signals
   - Recent news summary
   - AI summary and market position

Use this when:
- You want fresh data (company situation may have changed)
- Enrichment was skipped or incomplete
- Company recently announced major news (funding, acquisition, expansion)

---

### 5. Scoring Leads

#### Automatic Scoring
- Happens when you discover leads with **Auto-score** checked
- Happens when you add a manual lead with auto-analysis

#### Manual Re-scoring
1. Go to **Leads** tab
2. Click **Score All** to score all unscored leads, OR
3. Go to **Lead Detail** and click **Score** to re-score individual lead

Scoring evaluates:
- **Firmographic Score** (0–25): Company size, industry fit, funding stage
- **Title Score** (0–25): Decision-making authority, job level
- **Intent Score** (0–25): Buying signals, hiring, recent news
- **Engagement Score** (0–25): Budget authority qualification, ease of outreach

**Total Score**: 0–100
- 70+: **Hot** (ready for outreach)
- 45–69: **Warm** (research more, watch for signals)
- <45: **Cold** (not a fit right now)

---

### 6. Generating Outreach

#### Automatic Generation
- Available after lead is scored

#### Manual Generation
1. Go to **Lead Detail**
2. Click **Generate Outreach**
3. Claude creates 3 outreach sequences:

**LinkedIn Message** (Direct/connection message)
- Soft introduction
- Reference to company/role specifics
- No sales pitch
- Call to action: brief conversation

**Email Sequence** (3 emails)
- Email 1: Personalized introduction with value hook
- Email 2: Follow-up with proof point / case study
- Email 3: Final touch (leave door open, no more follows)

All messages are **draft status**. You can:
- Copy to CRM / email tool
- Customize before sending
- Mark as sent

---

## Technical Details

### Setup Requirements

#### Backend
```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
```

Set `.env`:
```
ANTHROPIC_API_KEY=sk-ant-xxxxx  # Your Claude API key
DATA_FILE=data/leads.json        # JSON storage location
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022  # Claude model
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

Runs on `http://localhost:5173`

#### API
Backend runs on `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### Key Endpoints

All requests go to `/api/leads/`:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/discover` | Discover new leads via web search |
| POST | `/` | Create + auto-analyse lead manually |
| GET | `/` | List all leads |
| GET | `/{id}` | Get lead details + score + outreach |
| POST | `/{id}/score` | Score/re-score a lead |
| POST | `/{id}/enrich` | Enrich/re-enrich a lead |
| POST | `/{id}/outreach` | Generate outreach messages |
| DELETE | `/{id}` | Delete a lead |

### JSON Structure

`leads.json` contains:

```json
{
  "leads": [
    {
      "id": "uuid",
      "first_name": "...",
      "last_name": "...",
      "email": "...",
      "title": "...",
      "company": "...",
      "company_size": "...",
      "industry": "...",
      "location": "...",
      "linkedin_url": "...",
      "website": "...",
      "ai_summary": "...",  // Claude-generated company summary
      "growth_stage": "...",
      "market_position": "...",
      "enrichment_confidence": 0-100,
      "buying_signals": [...],
      "pain_points": [...],
      "tech_stack": [...],
      "extra_data": {...},  // Additional enrichment data
      "status": "new|scored|outreach_ready|contacted",
      "source": "manual|claude_discover",
      "created_at": "ISO datetime",
      "updated_at": "ISO datetime"
    }
  ],
  "scores": {
    "lead_id": {
      "id": "score_uuid",
      "lead_id": "...",
      "total_score": 0-100,
      "firmographic_score": 0-25,
      "title_score": 0-25,
      "intent_score": 0-25,
      "engagement_score": 0-25,
      "priority": "hot|warm|cold",
      "icp_match": "Excellent|Good|Partial|Poor",
      "buying_stage": "Decision|Evaluation|Consideration|Awareness",
      "confidence": 0-100,
      "reasoning": "...",
      "next_best_action": "...",
      "scored_at": "ISO datetime"
    }
  },
  "outreach": {
    "lead_id": [
      {
        "id": "outreach_uuid",
        "lead_id": "...",
        "type": "linkedin|email",
        "subject": "...",  // Email subject (null for LinkedIn)
        "body": "...",
        "sequence_step": 1|2|3,
        "status": "draft|sent",
        "created_at": "ISO datetime"
      }
    ]
  }
}
```

---

## Best Practices

### For Better Lead Discovery

1. **Be specific about geography**: "Germany and France" not "Europe"
2. **Include company stage**: "Series A/B startups" or "500–5000 employee mid-market"
3. **Name the decision maker level**: "VP Engineering", "Director of Data", "CTO"
4. **Include relevant signals**: "actively hiring" or "recently funded" or "using Kubernetes"
5. **Keep it 1–2 sentences**: Too much detail confuses Claude; let web search discover

### For Better Scoring

1. **Provide complete lead info**: Title, company, location help accuracy
2. **Auto-enrich first**: Better enrichment = more accurate scores
3. **Check "next_best_action"**: Claude tells you exactly what to do next
4. **Re-score after news**: Major announcements change fit significantly

### For Better Outreach

1. **Personalize before sending**: Copy-paste and add specific details
2. **Space out emails**: Don't send 3 emails in 1 day
3. **Track responses**: Mark as "sent" in the UI
4. **Update status**: Mark as "contacted" after first touch

---

## Troubleshooting

### "API key is missing or invalid"
- Check `.env` has valid `ANTHROPIC_API_KEY`
- Restart backend after changing `.env`

### "Claude is searching…" takes >2 minutes
- Normal for 20+ leads or complex queries
- Check internet connection
- Consider reducing `max_leads` and running again

### Discovered leads have missing data
- Leads found but info not publicly available
- Manual fields (email, LinkedIn URL) may be empty = research separately
- Enrichment data helps fill gaps; run enrichment if empty

### Same lead discovered twice
- System checks for duplicates by email + name + company
- If email is missing, may create duplicate
- Manually delete via lead detail page

### Leads not saving
- Check `data/leads.json` has write permissions
- Check disk has space
- Check `DATA_FILE` path in `.env` exists

---

## Next Steps

1. **Get API key**: Sign up at [console.anthropic.com](https://console.anthropic.com) and create API key
2. **Update `.env`**: Add key to `backend/.env`
3. **Start backend**: `cd backend && python -m uvicorn app.main:app --reload`
4. **Start frontend**: `cd frontend && npm run dev`
5. **Try Discover**: Click Discover tab and describe your ideal lead
6. **Review results**: Check Leads tab for discovered leads
7. **Generate outreach**: Click a lead and generate LinkedIn + email messages

---

## FAQ

**Q: Is lead data really from Claude AI, or is there fallback mock data?**
A: All lead data is 100% from Claude + web search. No mock data, no fallback. If Claude can't find something, the field is empty.

**Q: How much does this cost?**
A: Costs depend on Anthropic API pricing. Discovery with auto-enrich/score is ~$0.10–0.30 per lead (varies by complexity).

**Q: Can I use this for other industries?**
A: Yes! The system works for any industry/geography/company stage. Just describe your target clearly.

**Q: How often should I re-enrich a lead?**
A: Re-enrich if: lead score changes, company announced major news, or it's been 30+ days. Otherwise, enrichment is good for 60–90 days.

**Q: Can I export leads to CSV?**
A: Not yet, but `leads.json` is human-readable. You can copy/paste data or build an export feature.

**Q: What if Claude makes a mistake in enrichment?**
A: All data is web-searched (verifiable). If inaccurate, web search results were likely wrong. Manually verify via company website or LinkedIn.

**Q: Can I schedule recurring lead discovery?**
A: Not built-in. Run manually via UI, or build a scheduler calling `/api/leads/discover` endpoint.

---

## Support & Feedback

Found a bug? Want a feature?
- Check system logs: `backend.log` (if enabled)
- Review Claude response in Anthropic dashboard
- Share feedback on improvement ideas
