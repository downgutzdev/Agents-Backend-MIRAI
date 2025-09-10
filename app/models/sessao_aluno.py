import uuid
from sqlalchemy import Column, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from database import Base

class SessaoAluno(Base):
    __tablename__ = "sessao_aluno"
    __table_args__ = {"schema": "public"}  # ou seu schema real

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    id_estudante = Column(UUID(as_uuid=True), nullable=False, index=True)
    strong_points = Column(Text, nullable=True)
    weak_points = Column(Text, nullable=True)
    general_comments = Column(Text, nullable=True)
    tema = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return (
            f"<SessaoAluno(uuid={self.uuid}, id_estudante={self.id_estudante}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})>"
        )
