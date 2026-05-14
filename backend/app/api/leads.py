"""
leads.py - JSON-backed lead API routes
All AI operations powered 100% by Claude. No mock data.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.core.json_store import (
    init_store,
    new_lead,
    new_outreach,
    new_score,
    read_store,
    update_lead,
    write_store,
)
from app.services.anthropic_client import ClaudeServiceError
from app.services.claude_lead_finder import find_leads_with_claude
from app.services.claude_service import analyse_lead_with_web, enrich_lead_with_web, generate_outreach, score_lead

router = APIRouter(prefix="/api/leads", tags=["leads"])


class LeadCreate(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    linkedin_url: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = "manual"


class DiscoverRequest(BaseModel):
    target: str
    max_leads: int = 10
    auto_enrich: bool = False
    auto_score: bool = False


def _score_summary(score: Optional[dict]) -> Optional[dict]:
    if not score:
        return None
    return {
        "total_score": score.get("total_score"),
        "priority": score.get("priority"),
        "icp_match": score.get("icp_match"),
        "confidence": score.get("confidence"),
        "buying_stage": score.get("buying_stage"),
    }


def _find_lead(store: dict, lead_id: str) -> Optional[dict]:
    return next((lead for lead in store["leads"] if lead["id"] == lead_id), None)


def _apply_enrichment(lead: dict, enriched: dict) -> None:
    if not enriched:
        return
    merged_extra = {**(lead.get("extra_data") or {}), **enriched}
    update_lead(
        lead,
        {
            "extra_data": merged_extra,
            "ai_summary": enriched.get("ai_summary"),
            "growth_stage": enriched.get("growth_stage"),
            "market_position": enriched.get("market_position"),
            "enrichment_confidence": enriched.get("enrichment_confidence"),
            "buying_signals": enriched.get("buying_signals", []) or [],
            "pain_points": enriched.get("pain_points", []) or [],
            "tech_stack": enriched.get("tech_stack", []) or [],
            "industry": enriched.get("industry") or lead.get("industry"),
            "company_size": enriched.get("company_size") or lead.get("company_size"),
        },
    )


def _normalise_score(score_data: dict) -> dict:
    score_data.setdefault("confidence", 0)
    score_data.setdefault("buying_stage", "unknown")
    score_data.setdefault("next_best_action", "")
    return score_data


def _raise_claude_http_error(exc: ClaudeServiceError) -> None:
    raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.on_event("startup")
async def setup_json_store():
    await init_store()


@router.get("/", response_model=List[dict])
async def list_leads():
    store = await read_store()
    leads = sorted(store["leads"], key=lambda lead: lead.get("created_at", ""), reverse=True)
    return [{**lead, "score": _score_summary(store["scores"].get(lead["id"]))} for lead in leads]


@router.post("/", response_model=dict)
async def create_lead(data: LeadCreate):
    store = await read_store()
    lead = new_lead(data.model_dump())
    store["leads"].append(lead)

    try:
        lead_data = dict(lead)
        analysis = await analyse_lead_with_web(lead_data)
        enriched = analysis.get("enrichment", {})
        _apply_enrichment(lead, enriched)

        score_data = _normalise_score(analysis.get("score", {}))
        store["scores"][lead["id"]] = new_score(lead["id"], score_data)
        update_lead(lead, {"status": "scored"})
    except ClaudeServiceError as exc:
        _raise_claude_http_error(exc)

    await write_store(store)
    return {
        "id": lead["id"],
        "message": "Lead created and analysed by Claude",
        "score": score_data,
        "enrichment": enriched,
    }


@router.post("/discover", response_model=dict)
async def discover_leads(req: DiscoverRequest):
    max_leads = max(1, min(req.max_leads, 25))
    try:
        discovery = await find_leads_with_claude(req.target, max_leads)
    except ClaudeServiceError as exc:
        _raise_claude_http_error(exc)
    found_leads = discovery.get("leads", [])
    search_summary = discovery.get("search_summary", "")

    store = await read_store()
    saved = []
    skipped = []

    for lead_raw in found_leads:
        email = lead_raw.get("email") or None
        if email and any(existing.get("email") == email for existing in store["leads"]):
            skipped.append({"reason": "duplicate email", "email": email})
            continue

        fname = lead_raw.get("first_name", "")
        lname = lead_raw.get("last_name", "")
        company = lead_raw.get("company", "")
        duplicate = any(
            existing.get("first_name") == fname
            and existing.get("last_name") == lname
            and existing.get("company") == company
            for existing in store["leads"]
        )
        if duplicate:
            skipped.append({"reason": "duplicate name+company", "name": f"{fname} {lname}"})
            continue

        lead = new_lead(
            {
                "first_name": fname,
                "last_name": lname,
                "email": email,
                "title": lead_raw.get("title"),
                "company": company,
                "industry": lead_raw.get("industry"),
                "company_size": lead_raw.get("company_size"),
                "location": lead_raw.get("location"),
                "linkedin_url": lead_raw.get("linkedin_url") or None,
                "source": "claude_discover",
                "extra_data": {"relevance_note": lead_raw.get("relevance_note", "")},
            }
        )
        store["leads"].append(lead)

        lead_data = dict(lead)
        enriched = {}
        score_data = {}

        try:
            if req.auto_enrich:
                enriched = await enrich_lead_with_web(lead_data)
                _apply_enrichment(lead, enriched)

            if req.auto_score:
                score_data = _normalise_score(await score_lead({**lead_data, "enrichment": enriched}))
                store["scores"][lead["id"]] = new_score(lead["id"], score_data)
                update_lead(lead, {"status": "scored"})
        except ClaudeServiceError as exc:
            _raise_claude_http_error(exc)

        saved.append(
            {
                "id": lead["id"],
                "name": f"{fname} {lname}",
                "company": company,
                "score": score_data.get("total_score"),
                "priority": score_data.get("priority"),
            }
        )

    await write_store(store)
    return {
        "message": f"Claude discovered {len(saved)} new leads from web search",
        "search_summary": search_summary,
        "target": req.target,
        "discovered": len(found_leads),
        "saved": len(saved),
        "skipped": len(skipped),
        "leads": saved,
    }


@router.get("/{lead_id}", response_model=dict)
async def get_lead(lead_id: str):
    store = await read_store()
    lead = _find_lead(store, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    return {
        "lead": lead,
        "score": store["scores"].get(lead_id),
        "outreach": store["outreach"].get(lead_id, []),
    }


@router.post("/{lead_id}/score", response_model=dict)
async def score_lead_route(lead_id: str):
    store = await read_store()
    lead = _find_lead(store, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    try:
        score_data = _normalise_score(await score_lead({**lead, "enrichment": lead.get("extra_data") or {}}))
    except ClaudeServiceError as exc:
        _raise_claude_http_error(exc)
    previous_score = store["scores"].get(lead_id)
    updated_score = new_score(lead_id, score_data)
    if previous_score:
        updated_score["id"] = previous_score["id"]
    store["scores"][lead_id] = updated_score
    update_lead(lead, {"status": "scored"})

    await write_store(store)
    return {"score": score_data}


@router.post("/{lead_id}/enrich", response_model=dict)
async def enrich_lead_route(lead_id: str, refresh: bool = Query(False, description="Force refresh even if already enriched")):
    store = await read_store()
    lead = _find_lead(store, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if lead.get("extra_data") and lead.get("ai_summary") and not refresh:
        return {"enriched": lead["extra_data"], "cached": True}

    try:
        enriched = await enrich_lead_with_web(dict(lead))
    except ClaudeServiceError as exc:
        _raise_claude_http_error(exc)
    _apply_enrichment(lead, enriched)
    await write_store(store)
    return {"enriched": enriched, "cached": False}


@router.post("/{lead_id}/outreach", response_model=dict)
async def generate_outreach_route(lead_id: str):
    store = await read_store()
    lead = _find_lead(store, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    score_data = store["scores"].get(lead_id, {})
    try:
        outreach_data = await generate_outreach({**lead, "enrichment": lead.get("extra_data") or {}}, score_data)
    except ClaudeServiceError as exc:
        _raise_claude_http_error(exc)

    type_map = {
        "linkedin_message": ("linkedin", 1),
        "email_step1": ("email", 1),
        "email_step2": ("email", 2),
        "email_step3": ("email", 3),
    }
    store["outreach"][lead_id] = [
        new_outreach(lead_id, outreach_type, step, outreach_data.get(key, {}))
        for key, (outreach_type, step) in type_map.items()
    ]
    update_lead(lead, {"status": "outreach_ready"})

    await write_store(store)
    return {"outreach": outreach_data}


@router.delete("/{lead_id}")
async def delete_lead(lead_id: str):
    store = await read_store()
    lead = _find_lead(store, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    store["leads"] = [item for item in store["leads"] if item["id"] != lead_id]
    store["scores"].pop(lead_id, None)
    store["outreach"].pop(lead_id, None)
    await write_store(store)
    return {"message": "Deleted"}
