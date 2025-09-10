# app/utils/triggers.py
from typing import Any, Dict, Optional

# Local workflows
from app.workflows.normal_session import run_natural_session
from app.workflows.class_session import run_class_session
from app.workflows.generate_query import run_generate_query  # <- local workflow (fake analytics)

# Fallback for direct calls (if some intent has no dedicated workflow)
from app.utils.agent_client import post_agent

# Intent → workflow (prefer workflows when available)
INTENT_TO_WORKFLOW = {
    "normal_session": "normal_session",
    "class_session":  "class_session",
    "generate_query": "generate_query",  # main intent for fake mode
    "generate_sql":   "generate_query",  # optional alias (compatibility)
}

# Intent → agent (only for fallback)
INTENT_TO_AGENT = {
    "normal_session": "natural_agent",
    "class_session":  "professor",  # used only as fallback (default is workflow)
    # We don’t map 'generate_query' to an agent because it’s local (fake)
}

def execute_workflow(
    intent: str,
    *,
    user_text: str,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Executes the flow corresponding to the intent:
      1) If there is a dedicated workflow → run local workflow.
      2) Otherwise, fall back to a direct call via post_agent.
    """
    context = context or {}

    # === Dedicated workflows ===
    if INTENT_TO_WORKFLOW.get(intent) == "normal_session":
        res = run_natural_session(session_id=session_id or "default_session", question=user_text)
        return {"status": "ok", "workflow": "normal_session", "result": res}

    if INTENT_TO_WORKFLOW.get(intent) == "class_session":
        aluno_uuid = context.get("aluno_uuid") or context.get("user_uuid") or context.get("user_id") or "generic_student"
        res = run_class_session(aluno_uuid=aluno_uuid, question=user_text, session_id=session_id or "default_session")
        return {"status": "ok", "workflow": "class_session", "result": res}

    if INTENT_TO_WORKFLOW.get(intent) == "generate_query":
        # Local analytics workflow (fake), no external agent:
        res = run_generate_query(
            question=user_text,
            user_id=user_id,
            session_id=session_id,
            context=context,   # must include user_uuid here for individual queries
        )
        return {"status": "ok", "workflow": "generate_query", "result": res}

    # === Fallback via agent ===
    agent_key = INTENT_TO_AGENT.get(intent)
    if not agent_key:
        return {"status": "error", "error": f"Workflow/Agent not found for intent '{intent}'."}

    payload = {
        "question": user_text,
        "user_id": user_id,
        "session_id": session_id,
        "context": context,
        "metadata": {"intent": intent},
    }
    payload = {k: v for k, v in payload.items() if v is not None}

    data = post_agent(agent_key, payload)
    return {"status": "ok", "workflow": intent, "result": data}
