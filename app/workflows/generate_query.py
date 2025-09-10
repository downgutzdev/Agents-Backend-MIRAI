# app/workflows/generate_query.py
from __future__ import annotations
from typing import Optional, Dict, Any, List
import re
from datetime import datetime
from app.data.fake_db import SESSOES_ALUNO


def _require_user_uuid(context: Dict[str, Any]) -> str:
    """
    Get the user (student) identifier from the given context.
    Accepts 'user_uuid', 'user_id', or 'aluno_uuid'. Raises if missing.
    """
    uid = (context.get("user_uuid")
           or context.get("user_id")
           or context.get("aluno_uuid"))
    if not uid:
        raise ValueError("Missing user_uuid in context for individual queries.")
    return uid


def _parse_top_n(text: str, default: int = 5) -> int:
    """
    Extract an integer N from free text; clamp to [1, 50]. Fallback to default.
    """
    m = re.search(r"\b(\d+)\b", text)
    if not m:
        return default
    try:
        n = int(m.group(1))
        return max(1, min(n, 50))
    except Exception:
        return default


def _last_sessions_for_user(user_uuid: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Return the last 'limit' sessions for the user, ordered by created_at desc.

    Note: 'created_at' is a string "YYYY-MM-DD HH:MM:SS". Sorting by string
    works for this format; for extra safety we could parse to datetime,
    but we keep it simple here.
    """
    rows = [s for s in SESSOES_ALUNO if s["id_estudante"] == user_uuid]
    rows.sort(key=lambda x: x["created_at"], reverse=True)
    return rows[:limit]


def _aggregate_points(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate strong/weak points, comments, and themes across sessions.
    No heavy NLP: just unique concatenation.
    """
    strong, weak, comments, temas = [], [], [], []
    seen_s, seen_w, seen_c, seen_t = set(), set(), set(), set()
    for r in rows:
        sp = (r.get("strong_points") or "").strip()
        wp = (r.get("weak_points") or "").strip()
        gc = (r.get("general_comments") or "").strip()
        tm = (r.get("tema") or "").strip()
        if sp and sp not in seen_s:
            strong.append(sp); seen_s.add(sp)
        if wp and wp not in seen_w:
            weak.append(wp); seen_w.add(wp)
        if gc and gc not in seen_c:
            comments.append(gc); seen_c.add(gc)
        if tm and tm not in seen_t:
            temas.append(tm); seen_t.add(tm)
    return {
        "strong_points": " • ".join(strong),
        "weak_points": " • ".join(weak),
        "general_comments": " | ".join(comments),
        # Keep 'temas' key/name for compatibility with the rest of the stack
        "temas": " • ".join(temas) if temas else "",
    }


def run_generate_query(
    question: str,
    *,
    user_id: Optional[str] = None,          # kept for ecosystem defaults
    session_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    **_ignored: Any,                        # swallow extra kwargs (robust)
) -> Dict[str, Any]:
    """
    Answer INDIVIDUAL analytical questions using fake data (SESSOES_ALUNO).
    Standard return: {status, kind, columns, rows, meta}

    Supported examples (PT):
      - "Qual é a minha última sessão?"
      - "Quero um resumo das minhas sessões (5)"
      - "Quero ver meus pontos fortes e fracos (3)"
      - "Quais são os temas mais frequentes (3)?"

    Supported examples (EN):
      - "What is my last session?"
      - "Give me a summary of my sessions (5)"
      - "Show my strengths and weaknesses (3)"
      - "What are the most frequent themes (3)?"
    """
    context = context or {}
    text = (question or "").strip().lower()

    # -------------------------
    # 1) "my last session"
    #    PT: (minha|meu) ... (última|ultima) ... sessão
    #    EN: my ... last ... session
    # -------------------------
    if (
        re.search(r"\b(minha|meu)\b.*\b(última|ultima)\b.*\bsess[aã]o", text)
        or re.search(r"\bmy\b.*\blast\b.*\bsession\b", text)
    ):
        uid = _require_user_uuid(context)
        last = _last_sessions_for_user(uid, limit=1)
        if not last:
            return {
                "status": "ok",
                "kind": "last_session",
                "columns": [],
                "rows": [],
                "meta": {"user_uuid": uid, "found": 0, "simulated": True},
            }
        s = last[0]
        # Keep column/field names that other components expect (Portuguese keys)
        columns = ["uuid", "tema", "strong_points", "weak_points", "general_comments", "created_at"]
        rows = [[s["uuid"], s["tema"], s["strong_points"], s["weak_points"], s["general_comments"], s["created_at"]]]
        return {
            "status": "ok",
            "kind": "last_session",
            "columns": columns,
            "rows": rows,
            "meta": {"user_uuid": uid, "found": 1, "simulated": True},
        }

    # -------------------------
    # 2) "summary of my sessions (N)"
    #    PT: (resumo|minhas) ... sessão
    #    EN: (summary|summarize) ... (my|of my) ... sessions
    # -------------------------
    if (
        re.search(r"\b(resumo|minhas)\b.*\bsess[aã]o", text)
        or re.search(r"\b(summary|summarize)\b.*\b(my|of my)\b.*\bsessions?\b", text)
    ):
        uid = _require_user_uuid(context)
        top_n = _parse_top_n(text, default=5)
        rows = _last_sessions_for_user(uid, limit=top_n)
        # Keep column names as-is for compatibility
        columns = ["created_at", "tema", "strong_points", "weak_points", "general_comments"]
        data = [[r["created_at"], r["tema"], r["strong_points"], r["weak_points"], r["general_comments"]] for r in rows]
        return {
            "status": "ok",
            "kind": "sessions_summary",
            "columns": columns,
            "rows": data,
            "meta": {"user_uuid": uid, "limit": top_n, "found": len(rows), "simulated": True},
        }

    # -------------------------
    # 3) "my strengths/weaknesses (N)"
    #    PT: (meus|minhas) ... (pontos fortes|pontos fracos|forças|fraquezas)
    #    EN: my ... (strengths|weaknesses|strong points|weak points)
    # -------------------------
    if (
        re.search(r"\b(meus|minhas)\b.*\b(pontos fortes|pontos fracos|forças|fraquezas)", text)
        or re.search(r"\bmy\b.*\b(strengths|weaknesses|strong points|weak points)\b", text)
    ):
        uid = _require_user_uuid(context)
        top_n = _parse_top_n(text, default=5)
        rows = _last_sessions_for_user(uid, limit=top_n)
        agg = _aggregate_points(rows)
        columns = ["strong_points", "weak_points", "general_comments", "temas"]  # keep 'temas'
        data = [[agg["strong_points"], agg["weak_points"], agg["general_comments"], agg["temas"]]]
        return {
            "status": "ok",
            "kind": "my_points",
            "columns": columns,
            "rows": data,
            "meta": {"user_uuid": uid, "limit": top_n, "found": len(rows), "simulated": True},
        }

    # -------------------------
    # 4) "most frequent themes (N)"
    #    PT: (tema|temas|assunto|assuntos) ... (frequentes|recorrentes|mais estudados)
    #    EN: (theme|themes|topic|topics) ... (frequent|most frequent|recurring|most studied)
    # -------------------------
    if (
        re.search(r"\b(temas?|assuntos?)\b.*\b(frequentes|recorrentes|mais estudados?)", text)
        or re.search(r"\b(themes?|topics?)\b.*\b(frequent|most frequent|recurring|most studied)\b", text)
    ):
        uid = _require_user_uuid(context)
        rows = _last_sessions_for_user(uid, limit=50)  # take a generous window
        freq: Dict[str, int] = {}
        for r in rows:
            t = (r.get("tema") or "").strip()
            if not t:
                continue
            freq[t] = freq.get(t, 0) + 1
        ordered = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
        top_n = _parse_top_n(text, default=5)
        top = ordered[:top_n]
        # Keep Portuguese column names as other parts may rely on them
        columns = ["tema", "ocorrencias"]
        data = [[tema, n] for (tema, n) in top]
        return {
            "status": "ok",
            "kind": "top_themes",
            "columns": columns,
            "rows": data,
            "meta": {"user_uuid": uid, "top_n": top_n, "simulated": True},
        }

    # Fallback (message translated to English)
    return {
        "status": "error",
        "message": (
            "Unsupported query (fake mode). Examples: "
            "'my last session', 'summary of my sessions (5)', "
            "'my strengths', 'most frequent themes (3)'. "
            "Also supported in Portuguese."
        ),
        "meta": {"simulated": True},
    }
