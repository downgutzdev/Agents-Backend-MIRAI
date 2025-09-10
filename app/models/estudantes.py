import uuid
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from database import Base

class Estudante(Base):
    __tablename__ = "estudante"
    __table_args__ = {"schema": "public"}  # ou seu schema real (ex: "educacional")

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    def __repr__(self):
        return f"<Estudante(uuid={self.uuid})>"
