# tests/test_workflows.py
from pprint import pprint
import requests
from typing import Optional, Dict, Any

from app.workflows.guardrails_session import run_guardrails_session
from app.utils.triggers import execute_workflow
from app.workflows.guardrails_runner import handle_user_message

HEALTH_URL = "http://127.0.0.1:9000/health"


# ----------------------------
# Helpers
# ----------------------------
def _ping_health(url: str = HEALTH_URL) -> bool:
    try:
        r = requests.get(url, timeout=3)
        print(f"[PING] {url} -> {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        print(f"[PING] Falhou: {e}")
        return False


def _run_guardrails_only(texto: str, user_id: str = "u123", session_id: str = "s123",
                         context: Optional[Dict[str, Any]] = None):
    print("\n[TEST] Guardrails → intent")
    res = run_guardrails_session(texto, user_id=user_id, session_id=session_id, context=context or {"source": "tests"})
    pprint(res)
    return res


def _run_trigger(intent: str, texto: str, user_id: str = "u123", session_id: str = "s123",
                 context: Optional[Dict[str, Any]] = None):
    print("\n[TEST] Trigger → agente correspondente")
    resp = execute_workflow(intent, user_text=texto, context=context or {"user_id": user_id},
                            user_id=user_id, session_id=session_id)
    pprint(resp)
    return resp


def _run_full_flow(texto: str, user_id: str = "u123", session_id: str = "s123",
                   context: Optional[Dict[str, Any]] = None):
    print("\n[TEST] Fluxo completo Guardrails → Trigger")
    out = handle_user_message(texto, context=context or {"user_id": user_id}, user_id=user_id, session_id=session_id)
    pprint(out)
    return out


# ----------------------------
# Testes (pytest)
# ----------------------------
def test_guardrails_ok():
    assert _ping_health(), "API não está de pé em http://127.0.0.1:9000/health"
    texto = "Quero apenas conversar sobre programação."
    res = _run_guardrails_only(texto)
    assert res.allowed is True
    assert res.intent == "normal_session"


def test_trigger_ok():
    assert _ping_health(), "API não está de pé em http://127.0.0.1:9000/health"
    texto = "Quero apenas conversar sobre programação."
    resp = _run_trigger("normal_session", texto)
    assert resp["status"] == "ok"
    assert resp["workflow"] == "normal_session"


def test_fluxo_completo_ok():
    assert _ping_health(), "API não está de pé em http://127.0.0.1:9000/health"
    texto = "Quero apenas conversar sobre programação."
    out = _run_full_flow(texto)
    assert out["final"]["status"] == "ok"
    assert out["guardrails"]["intent"] == "normal_session"


# ----------------------------
# Execução interativa (python -m tests.test_workflows)
# ----------------------------
if __name__ == "__main__":
    print("=== Modo interativo: Guardrails → Trigger ===")
    if not _ping_health():
        print("❌ API não está disponível. Suba o servidor: uvicorn main:app --reload --port 9000")
        raise SystemExit(1)

    pergunta = input("\nDigite sua pergunta: ").strip()
    if not pergunta:
        print("Nada digitado. Encerrando.")
        raise SystemExit(0)

    # 1) Guardrails
    gr = _run_guardrails_only(pergunta)

    # 2) Se bloqueado, encerra
    if not gr.allowed or not gr.intent:
        print("\n[FINAL] BLOQUEADO pelo guardrails.")
        raise SystemExit(0)

    # 3) Trigger (rota o intent para o agente)
    trig = _run_trigger(gr.intent, pergunta)

    # 4) Fluxo completo (apenas para demonstrar a orquestração integrada)
    full = _run_full_flow(pergunta)

    print("\n✅ Fim do fluxo interativo.")
