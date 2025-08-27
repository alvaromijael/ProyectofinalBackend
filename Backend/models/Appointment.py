import datetime
from sqlalchemy import Column, Integer, String, Date, Time, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from database.db import Base


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

    # Diagnosis (CIE-10)
    diagnosis_code = Column(String(10), nullable=True)
    diagnosis_description = Column(Text, nullable=True)

    # Observations and treatment
    observations = Column(Text, nullable=True)

    # Laboratory tests and studies
    laboratory_tests = Column(Text, nullable=True)

    # Vital signs
    temperature = Column(String(10), nullable=True)
    blood_pressure = Column(String(20), nullable=True)
    heart_rate = Column(String(10), nullable=True)
    oxygen_saturation = Column(String(10), nullable=True)
    weight = Column(String(10), nullable=True)
    height = Column(String(10), nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.datetime.utcnow)

    # Relationship to patient
    patient = relationship("Patient", back_populates="appointments")

# También necesitas agregar esta relación en tu modelo Patient:
# En el archivo models/Patient.py, agrega esta línea después de la relación contacts:
# appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")