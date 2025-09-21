import datetime
from sqlalchemy import Column, Integer, String, Date, Time, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from database.db import Base
from models.Recipe import Recipe


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = {"schema": "medical"}

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("medical.patients.id"), nullable=False, index=True)
    appointment_date = Column(Date, nullable=False, index=True)
    appointment_time = Column(Time, nullable=False)

    # Anamnesis
    current_illness = Column(Text, nullable=True)  # enfermedad actual

    # Physical examination
    physical_examination = Column(Text, nullable=True)

    # Observations and treatment
    observations = Column(Text, nullable=True)

    # Laboratory tests and studies
    laboratory_tests = Column(Text, nullable=True)

    # Vital signs
    temperature = Column(String(10), nullable=True)
    blood_pressure = Column(String(20), nullable=True)
    heart_rate = Column(String(10), nullable=True)
    oxygen_saturation = Column(String(10), nullable=True)
    weight = Column(Numeric(precision=6, scale=2), nullable=True)  # Valor numérico del peso
    weight_unit = Column(String(5), nullable=True, default="kg")   # Unidad: kg, lb, g
    height = Column(String(10), nullable=True)

    medical_preinscription = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    recipes = relationship("Recipe", back_populates="appointment", cascade="all, delete-orphan")
    diagnoses = relationship("AppointmentDiagnosis", back_populates="appointment", cascade="all, delete-orphan")


class AppointmentDiagnosis(Base):
    __tablename__ = "appointment_diagnoses"
    __table_args__ = {"schema": "medical"}

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("medical.appointments.id"), nullable=False, index=True)
    diagnosis_code = Column(String(10), nullable=False, index=True)
    diagnosis_description = Column(Text, nullable=False)
    diagnosis_type = Column(String(20), nullable=True, default="secondary")  # 'primary', 'secondary'
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    # Relationship
    appointment = relationship("Appointment", back_populates="diagnoses")