import json
import re


def safe_json_parse(text: str) -> dict:
    """
    Robustly parse JSON from Claude's response.
    Handles: raw JSON, ```json fences, extra text before/after JSON.
    """
    if not text:
        return {}

    # Strip markdown code fences
    text = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except Exception:
        pass

    # Find the first { ... } or [ ... ] block
    for start_char, end_char in [('{', '}'), ('[', ']')]:
        start = text.find(start_char)
        end = text.rfind(end_char)
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except Exception:
                pass

    return {}
