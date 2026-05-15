import anthropic

from app.core.config import settings
from app.utils.json_parser import safe_json_parse

WEB_SEARCH_TOOL = {
    "type": "web_search_20250305",
    "name": "web_search",
}


class ClaudeServiceError(Exception):
    pass


def _get_client() -> anthropic.AsyncAnthropic:
    api_key = (settings.ANTHROPIC_API_KEY or "").strip()
    if not api_key or api_key == "sk-ant-...":
        raise ClaudeServiceError(
            "ANTHROPIC_API_KEY is missing or still set to the placeholder. Update backend/.env with a valid Claude API key."
        )
    return anthropic.AsyncAnthropic(api_key=api_key)
 

def _extract_text(response) -> str:
    text = ""
    for block in response.content:
        if hasattr(block, "text") and block.text.strip():
            text = block.text
    return text

 
def _clean_result(result: dict) -> dict:
    for key in ["note", "warning", "disclaimer"]:
        result.pop(key, None)
    return result


def _api_error_detail(exc: anthropic.APIStatusError) -> str:
    body = exc.body if isinstance(exc.body, dict) else {}
    error = body.get("error", {}) if isinstance(body, dict) else {}
    message = error.get("message") if isinstance(error, dict) else None
    return message or exc.message or "Anthropic request failed."


async def _repair_json_response(raw_text: str) -> dict:
    client = _get_client()
    response = await client.messages.create(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=1200,
        system=(
            "You repair malformed model outputs. Return exactly one valid JSON object, no markdown, "
            "using only facts already present in the provided text."
        ),
        messages=[
            {
                "role": "user",
                "content": (
                    "Convert the following content into a valid JSON object. "
                    "If values are missing, use empty strings, empty arrays, or 0.\n\n"
                    f"{raw_text}"
                ),
            }
        ],
    )
    repaired = safe_json_parse(_extract_text(response))
    return repaired if isinstance(repaired, dict) else {}


async def run_claude_json_prompt(prompt: str, *, system_prompt: str, max_tokens: int) -> dict:
    client = _get_client()

    try:
        response = await client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            tools=[WEB_SEARCH_TOOL],
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.AuthenticationError as exc:
        raise ClaudeServiceError(
            "Anthropic rejected the configured API key. Update backend/.env with a valid Claude API key."
        ) from exc
    except anthropic.RateLimitError as exc:
        raise ClaudeServiceError(
            "Anthropic rate limited this request. Please wait a moment and try again."
        ) from exc
    except anthropic.APIConnectionError as exc:
        raise ClaudeServiceError(
            "Could not reach Anthropic. Check your internet connection and try again."
        ) from exc
    except anthropic.APIStatusError as exc:
        raise ClaudeServiceError(f"Anthropic request failed: {_api_error_detail(exc)}") from exc
    except anthropic.APIError as exc:
        raise ClaudeServiceError(f"Anthropic request failed: {exc.message}") from exc

    raw_text = _extract_text(response)
    result = safe_json_parse(raw_text)
    if (not isinstance(result, dict) or not result) and raw_text.strip():
        result = await _repair_json_response(raw_text)
    if not isinstance(result, dict) or not result:
        raise ClaudeServiceError(
            "Claude returned a response, but it was not valid JSON. Please retry the action."
        )

    return _clean_result(result)
