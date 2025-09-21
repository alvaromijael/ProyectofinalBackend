import datetime
from sqlalchemy import Column, Integer, String, Date, Text, DateTime
from sqlalchemy.orm import relationship
from database.db import Base
from models.Contact import Contact


class Patient(Base):
    __tablename__ = "patients"
    __table_args__ = {"schema": "medical"}

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    birth_date = Column(Date, nullable=True)
    gender = Column(String(20), nullable=False)
    document_id = Column(String(20), nullable=False, unique=True, index=True)
    marital_status = Column(String(50), nullable=True)
    occupation = Column(String(100), nullable=True)
    education = Column(String(100), nullable=True)
    origin = Column(String(100), nullable=True)
    province = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    medical_history = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    neighborhood = Column(String(100), nullable=True)
    street = Column(String(200), nullable=True)
    house_number = Column(String(20), nullable=True)
    created_at = Column(DateTime, nullable=True, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.datetime.utcnow)

    # Relation to contacts
    contacts = relationship(Contact, back_populates="patient", cascade="all, delete-orphan")

    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
