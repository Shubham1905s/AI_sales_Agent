import json
from asyncio import Lock
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.core.config import settings

_store_lock = Lock()

DEFAULT_STORE = {
    "leads": [],
    "scores": {},
    "outreach": {},
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _store_path() -> Path:
    return Path(settings.DATA_FILE).resolve()


def _ensure_store_exists() -> None:
    path = _store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps(DEFAULT_STORE, indent=2), encoding="utf-8")


def _load_store_sync() -> dict[str, Any]:
    _ensure_store_exists()
    path = _store_path()
    raw = json.loads(path.read_text(encoding="utf-8"))
    merged = deepcopy(DEFAULT_STORE)
    merged.update(raw)
    merged["scores"] = raw.get("scores", {}) or {}
    merged["outreach"] = raw.get("outreach", {}) or {}
    merged["leads"] = raw.get("leads", []) or []
    return merged


def _save_store_sync(store: dict[str, Any]) -> None:
    _ensure_store_exists()
    _store_path().write_text(json.dumps(store, indent=2), encoding="utf-8")


async def init_store() -> None:
    async with _store_lock:
        _ensure_store_exists()


async def read_store() -> dict[str, Any]:
    async with _store_lock:
        return deepcopy(_load_store_sync())


async def write_store(store: dict[str, Any]) -> dict[str, Any]:
    async with _store_lock:
        _save_store_sync(store)
        return deepcopy(store)


def new_lead(payload: dict[str, Any]) -> dict[str, Any]:
    now = _utc_now()
    return {
        "id": str(uuid4()),
        "first_name": payload.get("first_name", ""),
        "last_name": payload.get("last_name", ""),
        "email": payload.get("email"),
        "linkedin_url": payload.get("linkedin_url"),
        "title": payload.get("title"),
        "company": payload.get("company"),
        "company_size": payload.get("company_size"),
        "industry": payload.get("industry"),
        "location": payload.get("location"),
        "website": payload.get("website"),
        "phone": payload.get("phone"),
        "ai_summary": payload.get("ai_summary"),
        "growth_stage": payload.get("growth_stage"),
        "market_position": payload.get("market_position"),
        "enrichment_confidence": payload.get("enrichment_confidence"),
        "buying_signals": payload.get("buying_signals", []) or [],
        "pain_points": payload.get("pain_points", []) or [],
        "tech_stack": payload.get("tech_stack", []) or [],
        "extra_data": payload.get("extra_data", {}) or {},
        "status": payload.get("status", "new"),
        "source": payload.get("source", "manual"),
        "created_at": payload.get("created_at", now),
        "updated_at": payload.get("updated_at", now),
    }


def update_lead(lead: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    lead.update(updates)
    lead["updated_at"] = _utc_now()
    return lead


def new_score(lead_id: str, score_data: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(uuid4()),
        "lead_id": lead_id,
        "total_score": score_data.get("total_score", 0),
        "firmographic_score": score_data.get("firmographic_score", 0),
        "title_score": score_data.get("title_score", 0),
        "intent_score": score_data.get("intent_score", 0),
        "engagement_score": score_data.get("engagement_score", 0),
        "priority": score_data.get("priority", "cold"),
        "icp_match": score_data.get("icp_match"),
        "buying_stage": score_data.get("buying_stage", "unknown"),
        "confidence": score_data.get("confidence", 0),
        "next_best_action": score_data.get("next_best_action", ""),
        "reasoning": score_data.get("reasoning"),
        "scored_at": _utc_now(),
    }


def new_outreach(lead_id: str, outreach_type: str, sequence_step: int, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(uuid4()),
        "lead_id": lead_id,
        "type": outreach_type,
        "subject": payload.get("subject"),
        "body": payload.get("body", ""),
        "sequence_step": sequence_step,
        "status": "draft",
        "created_at": _utc_now(),
    }
