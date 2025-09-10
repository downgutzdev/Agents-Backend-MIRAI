# tests/test_fake_query_workflow.py
from pprint import pprint
import requests
from app.utils.triggers import execute_workflow

HEALTH_URL = "http://127.0.0.1:9000/health"
USER_UUID = "22222222-2222-2222-2222-222222222222"  # tem sessões no fake_db

def _ping_health(url: str = HEALTH_URL) -> bool:
    try:
        r = requests.get(url, timeout=3)
        print(f"[PING] {url} -> {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        print(f"[PING] Falhou: {e}")
        return False

def test_last_session():
    assert _ping_health()
    texto = "Qual é a minha última sessão?"
    ctx = {"user_uuid": USER_UUID}
    resp = execute_workflow("generate_query", user_text=texto, context=ctx, user_id=USER_UUID, session_id="s123")
    pprint(resp)
    assert resp["status"] == "ok" and resp["workflow"] == "generate_query"
    result = resp["result"]
    assert result["status"] == "ok" and result["kind"] == "last_session"
    assert result["columns"] and result["rows"] in ([], result["rows"])

def test_my_points_aggregate():
    assert _ping_health()
    texto = "Quero ver meus pontos fortes e fracos (5)"
    ctx = {"user_uuid": USER_UUID}
    resp = execute_workflow("generate_query", user_text=texto, context=ctx, user_id=USER_UUID, session_id="s123")
    pprint(resp)
    result = resp["result"]
    assert result["status"] == "ok" and result["kind"] == "my_points"
    assert result["columns"] == ["strong_points","weak_points","general_comments","temas"]
    assert isinstance(result["rows"], list) and len(result["rows"]) == 1

if __name__ == "__main__":
    print("=== Modo interativo: Fake Analytics Individual ===")
    if not _ping_health():
        print("❌ API não está disponível. Suba: uvicorn main:app --reload --port 9000")
        raise SystemExit(1)

    pergunta = input("\nPergunte (ex.: 'minha última sessão', 'meus pontos fortes (3)', 'temas mais frequentes (3)'): ").strip()
    ctx_uuid = input("Informe o user_uuid (ENTER p/ usar um com dados): ").strip() or USER_UUID

    out = execute_workflow(
        "generate_query",
        user_text=pergunta,
        context={"user_uuid": ctx_uuid},
        user_id=ctx_uuid,
        session_id="s123",
    )
    print("\n--- RESULTADO ---")
    pprint(out)
