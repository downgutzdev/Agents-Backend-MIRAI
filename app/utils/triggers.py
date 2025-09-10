# app/utils/triggers.py
from typing import Any, Dict, Optional

# Workflows locais
from app.workflows.normal_session import run_natural_session
from app.workflows.class_session import run_class_session
from app.workflows.generate_query import run_generate_query  # <- workflow local (fake analytics)

# Fallback para chamadas diretas (se algum intent não tiver workflow dedicado)
from app.utils.agent_client import post_agent

# Intent → workflow (preferimos workflows quando existem)
INTENT_TO_WORKFLOW = {
    "normal_session": "normal_session",
    "class_session":  "class_session",
    "generate_query": "generate_query",  # intent principal para o modo fake
    "generate_sql":   "generate_query",  # alias opcional (compat)
}

# Intent → agente (somente para fallback)
INTENT_TO_AGENT = {
    "normal_session": "natural_agent",
    "class_session":  "professor",  # usado só em fallback (o normal é workflow)
    # Não mapeamos 'generate_query' para agente porque é local (fake)
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
    Executa o fluxo correspondente ao intent:
      1) Se houver workflow dedicado → executa workflow local.
      2) Caso contrário, cai no fallback de chamada direta via post_agent.
    """
    context = context or {}

    # === Workflows dedicados ===
    if INTENT_TO_WORKFLOW.get(intent) == "normal_session":
        res = run_natural_session(session_id=session_id or "sessao_padrao", question=user_text)
        return {"status": "ok", "workflow": "normal_session", "result": res}

    if INTENT_TO_WORKFLOW.get(intent) == "class_session":
        aluno_uuid = context.get("aluno_uuid") or context.get("user_uuid") or context.get("user_id") or "aluno_generico"
        res = run_class_session(aluno_uuid=aluno_uuid, question=user_text, session_id=session_id or "sessao_padrao")
        return {"status": "ok", "workflow": "class_session", "result": res}

    if INTENT_TO_WORKFLOW.get(intent) == "generate_query":
        # Workflow local de analytics (fake), sem agente externo:
        res = run_generate_query(
            question=user_text,
            user_id=user_id,
            session_id=session_id,
            context=context,   # passe aqui o user_uuid para consultas individuais
        )
        return {"status": "ok", "workflow": "generate_query", "result": res}

    # === Fallback por agente ===
    agent_key = INTENT_TO_AGENT.get(intent)
    if not agent_key:
        return {"status": "error", "error": f"Workflow/Agente não encontrado para intent '{intent}'."}

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
