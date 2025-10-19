import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base


class Contact(Base):
    __tablename__ = "contacts"
    __table_args__ = {"schema": "medical"}

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("medical.patients.id"), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(120), nullable=True)
    relationship_type = Column(String(50), nullable=False)
    document_id = Column(String(20), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    # Relation to patient
    patient = relationship("Patient", back_populates="contacts")
