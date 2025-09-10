# app/data/fake_db.py
from __future__ import annotations
from typing import List, Dict, Any
from datetime import datetime, timedelta
import uuid

# ==== Students (only UUIDs, as in your Postgres) ====
STUDENTS: List[Dict[str, Any]] = [
    {"uuid": "11111111-1111-1111-1111-111111111111"},
    {"uuid": "22222222-2222-2222-2222-222222222222"},
    {"uuid": "33333333-3333-3333-3333-333333333333"},
    {"uuid": "44444444-4444-4444-4444-444444444444"},
    {"uuid": "55555555-5555-5555-5555-555555555555"},
    {"uuid": "66666666-6666-6666-6666-666666666666"},
    {"uuid": "77777777-7777-7777-7777-777777777777"},
    {"uuid": "88888888-8888-8888-8888-888888888888"},
    {"uuid": "99999999-9999-9999-9999-999999999999"},
    {"uuid": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"},
]

def _now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _days_ago(n: int) -> str:
    return (datetime.now() - timedelta(days=n)).strftime("%Y-%m-%d %H:%M:%S")

# ==== Student sessions (mirrors public.sessao_aluno) ====
# Fields: uuid, id_estudante, strong_points, weak_points, general_comments, tema, created_at, updated_at
SESSOES_ALUNO: List[Dict[str, Any]] = [
    {
        "uuid": str(uuid.uuid4()),
        "id_estudante": "22222222-2222-2222-2222-222222222222",
        "strong_points": "Programming",
        "weak_points": "Organization",
        "general_comments": "Participates actively.",
        "tema": "Basic Python",
        "created_at": _days_ago(1),
        "updated_at": _days_ago(1),
    },
    {
        "uuid": str(uuid.uuid4()),
        "id_estudante": "33333333-3333-3333-3333-333333333333",
        "strong_points": "Public speaking",
        "weak_points": "Calculus",
        "general_comments": "Good communication.",
        "tema": "Presentations",
        "created_at": _days_ago(3),
        "updated_at": _days_ago(3),
    },
    {
        "uuid": str(uuid.uuid4()),
        "id_estudante": "44444444-4444-4444-4444-444444444444",
        "strong_points": "English",
        "weak_points": "Focus",
        "general_comments": "Needs to improve concentration.",
        "tema": "Grammar",
        "created_at": _days_ago(4),
        "updated_at": _days_ago(4),
    },
    {
        "uuid": str(uuid.uuid4()),
        "id_estudante": "55555555-5555-5555-5555-555555555555",
        "strong_points": "Science",
        "weak_points": "Punctuality",
        "general_comments": "Shows curiosity.",
        "tema": "Biology",
        "created_at": _days_ago(7),
        "updated_at": _days_ago(7),
    },
    {
        "uuid": str(uuid.uuid4()),
        "id_estudante": "66666666-6666-6666-6666-666666666666",
        "strong_points": "Writing",
        "weak_points": "Mathematics",
        "general_comments": "Good narrative style.",
        "tema": "Literature",
        "created_at": _days_ago(9),
        "updated_at": _days_ago(9),
    },
    {
        "uuid": str(uuid.uuid4()),
        "id_estudante": "77777777-7777-7777-7777-777777777777",
        "strong_points": "Creativity",
        "weak_points": "Discipline",
        "general_comments": "Innovative ideas.",
        "tema": "Arts",
        "created_at": _days_ago(12),
        "updated_at": _days_ago(12),
    },
    {
        "uuid": str(uuid.uuid4()),
        "id_estudante": "88888888-8888-8888-8888-888888888888",
        "strong_points": "Logic",
        "weak_points": "Communication",
        "general_comments": "Good problem-solving skills.",
        "tema": "Algorithms",
        "created_at": _days_ago(15),
        "updated_at": _days_ago(15),
    },
    {
        "uuid": str(uuid.uuid4()),
        "id_estudante": "99999999-9999-9999-9999-999999999999",
        "strong_points": "Concentration",
        "weak_points": "Insecurity",
        "general_comments": "Hard-working.",
        "tema": "History",
        "created_at": _days_ago(20),
        "updated_at": _days_ago(20),
    },
    {
        "uuid": str(uuid.uuid4()),
        "id_estudante": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "strong_points": "Curiosity",
        "weak_points": "Anxiety",
        "general_comments": "Always asks questions.",
        "tema": "Philosophy",
        "created_at": _days_ago(21),
        "updated_at": _days_ago(21),
    },
]
