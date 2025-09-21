from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base


class Recipe(Base):
    __tablename__ = "recipe"
    __table_args__ = {"schema": "medical"}

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("medical.appointments.id"), nullable=False, index=True)
    medicine = Column(String(100), nullable=False)
    amount = Column(String(100), nullable=False)
    instructions = Column(String(500), nullable=False)
    lunchTime = Column(String(500), nullable=True)
    observations = Column(String(500), nullable=True)
    appointment = relationship("Appointment", back_populates="recipes")