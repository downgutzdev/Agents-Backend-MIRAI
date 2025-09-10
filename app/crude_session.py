# app/services/sessao_aluno_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.sessao_aluno import SessaoAluno
from app.models.estudantes import Estudante
import uuid

# C - CREATE
def create_sessao_aluno(db: Session, id_estudante, strong_points=None, weak_points=None, general_comments=None):
    obj = SessaoAluno(
        id_estudante=id_estudante,
        strong_points=strong_points,
        weak_points=weak_points,
        general_comments=general_comments,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

# R - READ (list all)
def get_all_sessoes(db: Session):
    return db.query(SessaoAluno).all()

# R - READ (by uuid)
def get_sessao_by_uuid(db: Session, sessao_uuid):
    return db.query(SessaoAluno).filter(SessaoAluno.uuid == sessao_uuid).first()

# R - READ (last global record)
def get_last_sessao(db: Session):
    return (
        db.query(SessaoAluno)
        .order_by(SessaoAluno.created_at.desc())
        .first()
    )

# U - UPDATE
def update_sessao_aluno(db: Session, sessao_uuid, **kwargs):
    sessao = db.query(SessaoAluno).filter(SessaoAluno.uuid == sessao_uuid).first()
    if not sessao:
        return None
    for key, value in kwargs.items():
        if hasattr(sessao, key):
            setattr(sessao, key, value)
    db.commit()
    db.refresh(sessao)
    return sessao

# D - DELETE
def delete_sessao_aluno(db: Session, sessao_uuid):
    sessao = db.query(SessaoAluno).filter(SessaoAluno.uuid == sessao_uuid).first()
    if not sessao:
        return False
    db.delete(sessao)
    db.commit()
    return True

# --- Local test script ---
if __name__ == "__main__":
    from dotenv import load_dotenv
    from database import SessionLocal

    load_dotenv()
    db = SessionLocal()

    fake_estudantes = [uuid.uuid4() for _ in range(3)]

    for id_estudante in fake_estudantes:
        db.execute(
            text("INSERT INTO estudante (uuid) VALUES (:uuid) ON CONFLICT DO NOTHING;"),
            {"uuid": str(id_estudante)}
        )
    db.commit()

    sessoes = []
    for i, id_estudante in enumerate(fake_estudantes):
        sessao = create_sessao_aluno(
            db,
            id_estudante=id_estudante,
            strong_points=f"Strong point {i+1}",
            weak_points=f"Weak point {i+1}",
            general_comments=f"Random comment {i+1}",
        )
        print(f"Session created: uuid={sessao.uuid}")
        sessoes.append(sessao)

    print("\nListing all sessions:")
    for s in get_all_sessoes(db):
        print(f"{s.uuid} | student: {s.id_estudante} | strong: {s.strong_points}")

    print("\nFetching last created session (global):")
    last = get_last_sessao(db)
    if last:
        print(f"Last session → {last.uuid} | student: {last.id_estudante} | strong: {last.strong_points}")

    db.close()
