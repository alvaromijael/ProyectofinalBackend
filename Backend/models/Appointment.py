import datetime
from sqlalchemy import Column, Integer, String, Date, Time, Text, DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship
from database.db import Base
from models.Recipe import Recipe


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = {"schema": "medical"}

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("medical.patients.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("auth.auth_users.id"), nullable=False, index=True)
    appointment_date = Column(Date, nullable=False, index=True)
    appointment_time = Column(Time, nullable=False)
    current_illness = Column(Text, nullable=True)
    physical_examination = Column(Text, nullable=True)
    observations = Column(Text, nullable=True)
    laboratory_tests = Column(Text, nullable=True)

    temperature = Column(String(10), nullable=True)
    blood_pressure = Column(String(20), nullable=True)
    heart_rate = Column(String(10), nullable=True)
    oxygen_saturation = Column(String(10), nullable=True)
    weight = Column(Numeric(precision=6, scale=2), nullable=True)  # Valor numérico del peso
    weight_unit = Column(String(5), nullable=True, default="kg")  # Unidad: kg, lb, g
    height = Column(String(10), nullable=True)
    has_representative = Column(Boolean, default=False, nullable=True)
    representative_id = Column(Integer, ForeignKey("medical.contacts.id"), nullable=True)
    contingency_type  = Column(String(100), nullable=True)
    medical_preinscription = Column(Text, nullable=True)

    sabbath_days = Column(Integer, nullable=True)
    rest_from = Column(Date, nullable=True)
    rest_to = Column(Date, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="appointments")
    recipes = relationship("Recipe", back_populates="appointment", cascade="all, delete-orphan")
    diagnoses = relationship("AppointmentDiagnosis", back_populates="appointment", cascade="all, delete-orphan")
    user = relationship("AuthUser", back_populates="appointments")



class AppointmentDiagnosis(Base):
    __tablename__ = "appointment_diagnoses"
    __table_args__ = {"schema": "medical"}

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("medical.appointments.id"), nullable=False, index=True)
    diagnosis_code = Column(String(10), nullable=False, index=True)
    diagnosis_description = Column(Text, nullable=False)
    diagnosis_type = Column(String(20), nullable=True, default="secondary")
    diagnosis_observations = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    appointment = relationship("Appointment", back_populates="diagnoses")