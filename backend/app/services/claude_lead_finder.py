from app.services.anthropic_client import run_claude_json_prompt

SYSTEM_PROMPT = """
You are an elite B2B sales intelligence agent with live web access.

Your job: given a natural language target description, find REAL companies
and REAL decision makers that match — using web search.

Rules:
- NEVER invent or fabricate company names, people, emails, or LinkedIn URLs
- Only return leads you actually found via web search
- If you cannot find a verified email, leave it as empty string
- If you cannot find a verified LinkedIn URL, leave it as empty string
- Always return valid JSON, nothing else
- No markdown, no code fences, no explanations outside the JSON
"""

FINDER_PROMPT_TEMPLATE = """
Target description:
"{target}"

Your task:
1. Search for companies in this space — look for company directories,
   LinkedIn company pages, news articles, and industry lists
2. For each promising company, search for decision makers by name + title
3. Search for any verified contact information

Find {max_leads} real leads. For each lead return:
- First and last name (real person you found)
- Their job title
- Company name
- Company industry
- Estimated company size (headcount range)
- Their LinkedIn profile URL if found (verify it exists)
- Their business email if found publicly
- Their work location (city, country)
- Why they are relevant to this target (1 sentence)

Return ONLY this JSON:
{{
  "leads": [
    {{
      "first_name": "",
      "last_name": "",
      "title": "",
      "company": "",
      "industry": "",
      "company_size": "",
      "linkedin_url": "",
      "email": "",
      "location": "",
      "relevance_note": "",
      "source": "claude_web_search"
    }}
  ],
  "search_summary": "brief note on what you searched and found"
}}
"""


async def find_leads_with_claude(target: str, max_leads: int = 10) -> dict:
    """
    Use Claude + web_search to find real leads matching the target description.
    Returns structured lead data — no mock, no fallback invented data.
    """
    prompt = FINDER_PROMPT_TEMPLATE.format(
        target=target,
        max_leads=max_leads
    )

    result = await run_claude_json_prompt(
        prompt,
        system_prompt=SYSTEM_PROMPT,
        max_tokens=2200,
    )

    leads = result.get("leads", [])
    summary = result.get("search_summary", "")

    # Sanitise — remove any lead with no first_name or company
    leads = [
        l for l in leads
        if l.get("first_name") and l.get("company")
    ]

    return {
        "leads": leads,
        "search_summary": summary,
        "total_found": len(leads)
    }
