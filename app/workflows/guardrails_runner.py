# app/workflows/guardrails_runner.py
from typing import Dict, Any, Optional
from app.workflows.guardrails_session import run_guardrails_session
from app.utils.triggers import execute_workflow

def handle_user_message(
    user_text: str,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    gr = run_guardrails_session(user_text, user_id=user_id, session_id=session_id, context=context)
    out: Dict[str, Any] = {
        "guardrails": {"allowed": gr.allowed, "intent": gr.intent, "reason": gr.reason, "raw": gr.raw}
    }
    if not gr.allowed or not gr.intent:
        out["final"] = {"status": "blocked", "message": gr.reason}
        return out

    trig = execute_workflow(gr.intent, user_text=user_text, context=context or {}, user_id=user_id, session_id=session_id)
    out["trigger"] = trig
    out["final"] = trig if trig.get("status") == "ok" else {"status": "error", "message": trig.get("error")}
    return out
