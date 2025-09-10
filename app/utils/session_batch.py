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
    """
    Join unique non-empty strings with '; ' without exceeding max_len.
    """
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
        add_len = len(it) + (2 if out else 0)  # accounts for "; "
        if total + add_len > max_len:
            break
        out.append(it)
        total += add_len
    return "; ".join(out)

def flatten_text(s: str) -> str:
    """Flattens whitespace (line breaks, tabs) to reduce tokens."""
    if not isinstance(s, str):
        return ""
    s = s.replace("\x00", " ").replace("\r", " ").replace("\t", " ")
    return re.sub(r"\s+", " ", s).strip()

def chunk_text(s: str, max_chars: int = 1800, overlap: int = 220) -> List[str]:
    """
    Splits a long text into chunks <= max_chars with overlap to avoid edge loss.
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
    """
    Merge multiple evaluation dicts into a compact, de-duplicated summary.
    """
    sp = _dedup_join([e.get("strong_points", "") for e in evals], max_len=450)
    wp = _dedup_join([e.get("weak_points", "") for e in evals], max_len=450)
    gc = _dedup_join([e.get("general_comments", "") for e in evals], max_len=600)
    return {
        "strong_points": sp,
        "weak_points":  wp,
        "general_comments": gc,
    }

def make_session_summary(merged_eval: Dict[str, str], last_turn: str) -> str:
    """
    Build a compact human-readable summary string of the session.
    """
    parts = []
    if merged_eval.get("strong_points"):
        parts.append(f"Strong points: {merged_eval['strong_points']}")
    if merged_eval.get("weak_points"):
        parts.append(f"Weak points: {merged_eval['weak_points']}")
    if merged_eval.get("general_comments"):
        parts.append(f"Comments: {merged_eval['general_comments']}")
    if last_turn:
        parts.append(f"Student's last question: {last_turn.strip()}")
    compact = " | ".join(parts)
    return compact[:1800]
