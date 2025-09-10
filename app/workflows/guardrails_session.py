# app/workflows/guardrails_session.py
from dataclasses import dataclass
from typing import Optional, Dict, Any
import json, re
from app.utils.agent_client import post_agent  # (no need for 'requests' here)

@dataclass
class GuardrailsResult:
    allowed: bool
    intent: Optional[str]
    reason: str
    raw: Dict[str, Any]

_CLASS_TO_INTENT = {
    "sessao_de_estudos":  "class_session",
    "conversa_com_query": "normal_session",
    "conversa_sem_query": "normal_session",
}

_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)

def _coerce_json(payload: Any) -> Dict[str, Any]:
    """
    Normalize the server response into a pure 'assessment' dict.
    Accepts:
      - {"assessment": {...}}
      - {...} (already the assessment body)
      - string containing JSON (with or without ```json fenced block)
    """
    if isinstance(payload, dict):
        # <<< UNWRAP IF COMES AS {"assessment": {...}} >>>
        return payload.get("assessment", payload)

    if isinstance(payload, str):
        m = _JSON_BLOCK_RE.search(payload)
        text = m.group(0) if m else payload
        data = json.loads(text)
        return data.get("assessment", data)

    raise ValueError("Guardrails response is neither dict nor JSON string.")

def run_guardrails_session(
    user_text: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> GuardrailsResult:
    payload = {
        "question": user_text,
        "user_id": user_id,
        "session_id": session_id,
        "context": context or {},
    }
    payload = {k: v for k, v in payload.items() if v is not None}

    # Call the agent
    data = post_agent("guardrails", payload)

    # <<< NEW: extract pure assessment, even if wrapped >>>
    res = _coerce_json(data)

    # compat: old typo
    if "pergunta_nocisva" in res and "pergunta_nociva" not in res:
        res["pergunta_nociva"] = res.pop("pergunta_nocisva")

    nociva = bool(res.get("pergunta_nociva", False))
    classe = (res.get("classificacao_pergunta") or "").strip().lower()

    intent  = _CLASS_TO_INTENT.get(classe)
    allowed = (not nociva) and (intent is not None)

    reason = (
        "Harmful question detected." if nociva else
        (f"Classification '{classe}' → intent '{intent}'." if intent else "Unmapped classification.")
    )

    return GuardrailsResult(allowed=allowed, intent=intent, reason=reason, raw=res)
