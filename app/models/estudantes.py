import uuid
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from database import Base

class Student(Base):
    __tablename__ = "estudante"  # keep original table name for DB compatibility
    __table_args__ = {"schema": "public"}  # or your actual schema (e.g., "educational")

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    def __repr__(self):
        return f"<Student(uuid={self.uuid})>"
