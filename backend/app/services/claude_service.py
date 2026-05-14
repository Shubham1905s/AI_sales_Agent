import json
from app.services.anthropic_client import run_claude_json_prompt

SYSTEM_PROMPT = """
You are an elite AI SDR and B2B sales intelligence system with live web access.

Core rules:
- Use web_search to find REAL, current information before answering
- NEVER fabricate company details, news, or personal information
- If you cannot find something, return empty string — not invented data
- Always return ONLY valid JSON — no markdown, no code fences, no commentary
- Numbers must be actual numbers (not strings), arrays must be arrays
"""


async def analyse_lead_with_web(lead_data: dict) -> dict:
    """
    Research and score a lead in a single Claude call to reduce latency and token usage.
    """
    company = lead_data.get("company", "")
    name = f"{lead_data.get('first_name', '')} {lead_data.get('last_name', '')}".strip()
    title = lead_data.get("title", "")
    website = lead_data.get("website", "")

    prompt = f"""
Research and score this B2B lead using web search, then return a single JSON object.

Lead:
{json.dumps(lead_data, indent=2)}

Search for:
- "{company} company", "{website or company} about", "{company} news 2025", "{company} hiring"
- "{company} funding" and "{company} technology stack"
- "{name} {company}", "{name} {title}", and "{name} LinkedIn"

Return ONLY this JSON:

{{
  "enrichment": {{
    "industry": "",
    "company_size": "",
    "funding_stage": "",
    "tech_stack": [],
    "pain_points": [],
    "buying_signals": [],
    "business_priorities": [],
    "growth_stage": "",
    "market_position": "",
    "recent_news_summary": "",
    "ai_summary": "",
    "enrichment_confidence": 0
  }},
  "score": {{
    "total_score": 0,
    "firmographic_score": 0,
    "title_score": 0,
    "intent_score": 0,
    "engagement_score": 0,
    "priority": "",
    "icp_match": "",
    "buying_stage": "",
    "confidence": 0,
    "reasoning": "",
    "next_best_action": ""
  }}
}}
"""

    result = await run_claude_json_prompt(
        prompt,
        system_prompt=SYSTEM_PROMPT,
        max_tokens=1600,
    )
    result.setdefault("enrichment", {})
    result.setdefault("score", {})
    return result


async def enrich_lead_with_web(lead_data: dict) -> dict:
    """
    Deep-research a lead using Claude + live web search.
    Searches for company news, hiring signals, funding, tech stack, and person context.
    Returns real intelligence — no invented data.
    """
    company = lead_data.get("company", "")
    name = f"{lead_data.get('first_name', '')} {lead_data.get('last_name', '')}".strip()
    title = lead_data.get("title", "")
    website = lead_data.get("website", "")

    prompt = f"""
Research this lead thoroughly using web search, then return structured intelligence.

Lead:
{json.dumps(lead_data, indent=2)}

Step 1 — Company research:
- Search "{company} company" and "{website or company} about" for industry, size, what they do
- Search "{company} funding" or "{company} investment 2024 2025" for funding signals
- Search "{company} news 2025" for recent announcements, product launches, expansions
- Search "{company} engineering jobs" or "{company} data jobs" for hiring signals

Step 2 — Person research:
- Search "{name} {company}" or "{name} {title}" for any public profile context
- Search "{name} LinkedIn" to find their profile URL

Step 3 — Tech intelligence:
- Search "{company} technology stack" or "{company} uses" to identify their tools

After searching, return ONLY this JSON. Use empty string "" if not found. Never invent data.

{{
  "industry": "",
  "company_size": "",
  "funding_stage": "",
  "tech_stack": [],
  "pain_points": [],
  "buying_signals": [],
  "business_priorities": [],
  "growth_stage": "",
  "market_position": "",
  "recent_news_summary": "",
  "ai_summary": "",
  "enrichment_confidence": 0
}}
"""

    result = await run_claude_json_prompt(
        prompt,
        system_prompt=SYSTEM_PROMPT,
        max_tokens=1200,
    )
    return result


async def score_lead(lead_data: dict) -> dict:
    """
    Score a lead 0–100 using Claude, backed by real web signals.
    Evaluates ICP fit, intent, buying stage, and urgency.
    """
    company = lead_data.get("company", "")

    prompt = f"""
Score this lead like a senior enterprise SDR who has just researched the account.

Lead data (may include enrichment from prior web research):
{json.dumps(lead_data, indent=2)}

If you need to verify any signals, search for "{company} news" or "{company} hiring 2025".

Evaluate:
- Firmographic fit: is this the right company type, size, and industry?
- Title/seniority: does this person have budget authority?
- Intent signals: are there hiring, funding, or expansion signals?
- Engagement indicators: how warm is this lead likely to be?

Scoring guide:
- total_score: 0–100 composite
- firmographic_score: 0–25
- title_score: 0–25
- intent_score: 0–25
- engagement_score: 0–25
- priority: "hot" (75+), "warm" (45–74), "cold" (<45)
- icp_match: "strong" | "moderate" | "weak"
- buying_stage: "awareness" | "consideration" | "decision" | "unknown"
- confidence: 0–100 (how confident you are in this score)

Return ONLY this JSON:

{{
  "total_score": 0,
  "firmographic_score": 0,
  "title_score": 0,
  "intent_score": 0,
  "engagement_score": 0,
  "priority": "",
  "icp_match": "",
  "buying_stage": "",
  "confidence": 0,
  "reasoning": "",
  "next_best_action": ""
}}
"""

    result = await run_claude_json_prompt(
        prompt,
        system_prompt=SYSTEM_PROMPT,
        max_tokens=900,
    )
    result.setdefault("confidence", 0)
    result.setdefault("buying_stage", "unknown")
    result.setdefault("next_best_action", "")
    return result


async def generate_outreach(lead_data: dict, score_data: dict) -> dict:
    """
    Generate personalised multi-touch outreach using Claude + live web search.
    Claude finds a real, current hook (recent post, news, or hiring signal)
    and builds outreach around it. No template filler.
    """
    company = lead_data.get("company", "")
    name = f"{lead_data.get('first_name', '')} {lead_data.get('last_name', '')}".strip()
    title = lead_data.get("title", "")

    prompt = f"""
Generate highly personalised B2B outreach for this lead.

Lead:
{json.dumps(lead_data, indent=2)}

Score context:
{json.dumps(score_data, indent=2)}

Step 1 — Find a real hook by searching:
- "{name} LinkedIn post" or "{name} {company} article" for something they recently wrote
- "{company} news 2025" or "{company} announcement" for a recent company event
- "{company} hiring {title.split()[0] if title else 'engineer'}" for a relevant job signal

Step 2 — Write the outreach:
- LinkedIn message: 3–4 sentences max. Open with the real hook you found. Connect it to a pain.
- Email step 1: Short hook email. Subject line must be specific, not generic.
- Email step 2 (Day 3): Follow-up with a quantified value prop (metric or case study angle).
- Email step 3 (Day 7): Light, respectful break-up — no pressure, leave door open.

Rules:
- Every message must reference something REAL you found (not generic praise)
- No "I hope this email finds you well", no "touch base", no "circle back"
- Natural, human tone — a colleague, not a vendor
- No placeholders like [COMPANY] or [NAME] — use the actual values

Return ONLY this JSON:

{{
  "linkedin_message": {{
    "body": ""
  }},
  "email_step1": {{
    "subject": "",
    "body": ""
  }},
  "email_step2": {{
    "subject": "",
    "body": ""
  }},
  "email_step3": {{
    "subject": "",
    "body": ""
  }}
}}
"""

    result = await run_claude_json_prompt(
        prompt,
        system_prompt=SYSTEM_PROMPT,
        max_tokens=1800,
    )
    return result
