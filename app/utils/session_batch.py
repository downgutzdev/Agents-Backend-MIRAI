# app/utils/session_batch.py
import re
from typing import List, Dict

__all__ = [
    "flatten_text",
    "chunk_text",
    "merge_evaluations",
    "make_session_summary",
]

def _dedup_join(items: List[str], max_len: int) -> str:
    seen = set()
    out = []
    total = 0
    for it in items:
        it = (it or "").strip()
        if not it:
            continue
        key = it.lower()
        if key in seen:
            continue
        seen.add(key)
        add_len = len(it) + (2 if out else 0)  # conta "; "
        if total + add_len > max_len:
            break
        out.append(it)
        total += add_len
    return "; ".join(out)

def flatten_text(s: str) -> str:
    """Achata whitespaces (quebras de linha, tabs) para reduzir tokens."""
    if not isinstance(s, str):
        return ""
    s = s.replace("\x00", " ").replace("\r", " ").replace("\t", " ")
    return re.sub(r"\s+", " ", s).strip()

def chunk_text(s: str, max_chars: int = 1800, overlap: int = 220) -> List[str]:
    """
    Fatia texto longo em blocos <= max_chars com overlap p/ evitar perda na borda.
    """
    s = s.strip()
    if len(s) <= max_chars:
        return [s]
    chunks = []
    i = 0
    n = len(s)
    while i < n:
        end = min(i + max_chars, n)
        chunks.append(s[i:end])
        if end == n:
            break
        i = max(end - overlap, i + 1)
    return chunks

def merge_evaluations(evals: List[Dict[str, str]]) -> Dict[str, str]:
    sp = _dedup_join([e.get("strong_points", "") for e in evals], max_len=450)
    wp = _dedup_join([e.get("weak_points", "") for e in evals], max_len=450)
    gc = _dedup_join([e.get("general_comments", "") for e in evals], max_len=600)
    return {
        "strong_points": sp,
        "weak_points":  wp,
        "general_comments": gc,
    }

def make_session_summary(merged_eval: Dict[str, str], last_turn: str) -> str:
    parts = []
    if merged_eval.get("strong_points"):
        parts.append(f"Pontos fortes: {merged_eval['strong_points']}")
    if merged_eval.get("weak_points"):
        parts.append(f"Pontos fracos: {merged_eval['weak_points']}")
    if merged_eval.get("general_comments"):
        parts.append(f"Comentários: {merged_eval['general_comments']}")
    if last_turn:
        parts.append(f"Última questão do aluno: {last_turn.strip()}")
    compact = " | ".join(parts)
    return compact[:1800]
