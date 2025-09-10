# app/data/fake_db.py
from __future__ import annotations
from typing import List, Dict, Any
from datetime import datetime, timedelta
import uuid

# ==== Estudantes (apenas UUIDs, como no seu Postgres) ====
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

# ==== Sessões do aluno (espelha public.sessao_aluno) ====
# Campos: uuid, id_estudante, strong_points, weak_points, general_comments, tema, created_at, updated_at
SESSOES_ALUNO: List[Dict[str, Any]] = [
    {
        "uuid": str(uuid.uuid4()),
        "id_estudante": "22222222-2222-2222-2222-222222222222",
        "strong_points": "Programação",
        "weak_points": "Organização",
        "general_comments": "Participa ativamente.",
        "tema": "Python Básico",
        "created_at": _days_ago(1),
        "updated_at": _days_ago(1),
    },
    {
        "uuid": str(uuid.uuid4()),
        "id_estudante": "33333333-3333-3333-3333-333333333333",
        "strong_points": "Oratória",
        "weak_points": "Cálculo",
        "general_comments": "Boa comunicação.",
        "tema": "Apresentações",
        "created_at": _days_ago(3),
        "updated_at": _days_ago(3),
    },
    {
        "uuid": str(uuid.uuid4()),
        "id_estudante": "44444444-4444-4444-4444-444444444444",
        "strong_points": "Inglês",
        "weak_points": "Foco",
        "general_comments": "Precisa melhorar a concentração.",
        "tema": "Gramática",
        "created_at": _days_ago(4),
        "updated_at": _days_ago(4),
    },
    {
        "uuid": str(uuid.uuid4()),
        "id_estudante": "55555555-5555-5555-5555-555555555555",
        "strong_points": "Ciências",
        "weak_points": "Pontualidade",
        "general_comments": "Demonstra curiosidade.",
        "tema": "Biologia",
        "created_at": _days_ago(7),
        "updated_at": _days_ago(7),
    },
    {
        "uuid": str(uuid.uuid4()),
        "id_estudante": "66666666-6666-6666-6666-666666666666",
        "strong_points": "Escrita",
        "weak_points": "Matemática",
        "general_comments": "Bom estilo narrativo.",
        "tema": "Literatura",
        "created_at": _days_ago(9),
        "updated_at": _days_ago(9),
    },
    {
        "uuid": str(uuid.uuid4()),
        "id_estudante": "77777777-7777-7777-7777-777777777777",
        "strong_points": "Criatividade",
        "weak_points": "Disciplina",
        "general_comments": "Ideias inovadoras.",
        "tema": "Artes",
        "created_at": _days_ago(12),
        "updated_at": _days_ago(12),
    },
    {
        "uuid": str(uuid.uuid4()),
        "id_estudante": "88888888-8888-8888-8888-888888888888",
        "strong_points": "Lógica",
        "weak_points": "Comunicação",
        "general_comments": "Boa resolução de problemas.",
        "tema": "Algoritmos",
        "created_at": _days_ago(15),
        "updated_at": _days_ago(15),
    },
    {
        "uuid": str(uuid.uuid4()),
        "id_estudante": "99999999-9999-9999-9999-999999999999",
        "strong_points": "Concentração",
        "weak_points": "Insegurança",
        "general_comments": "Esforçado.",
        "tema": "História",
        "created_at": _days_ago(20),
        "updated_at": _days_ago(20),
    },
    {
        "uuid": str(uuid.uuid4()),
        "id_estudante": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "strong_points": "Curiosidade",
        "weak_points": "Ansiedade",
        "general_comments": "Sempre faz perguntas.",
        "tema": "Filosofia",
        "created_at": _days_ago(21),
        "updated_at": _days_ago(21),
    },
]
