from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, time, datetime


class VitalSigns(BaseModel):
    temperature: Optional[str] = Field(None, description="Temperatura corporal en °C")
    blood_pressure: Optional[str] = Field(None, description="Presión arterial (ej: 120/80)")
    heart_rate: Optional[str] = Field(None, description="Frecuencia cardíaca en lpm")
    oxygen_saturation: Optional[str] = Field(None, description="Saturación de oxígeno en %")
    weight: Optional[str] = Field(None, description="Peso en kg")
    height: Optional[str] = Field(None, description="Talla en cm")


class DiagnosisInfo(BaseModel):
    code: Optional[str] = Field(None, description="Código CIE-10")
    description: Optional[str] = Field(None, description="Descripción del diagnóstico")


class AppointmentBase(BaseModel):
    patient_id: int = Field(..., description="ID del paciente")
    appointment_date: date = Field(..., description="Fecha de la cita")
    appointment_time: time = Field(..., description="Hora de la cita")
    current_illness: Optional[str] = Field(None, description="Enfermedad actual")
    physical_examination: Optional[str] = Field(None, description="Examen físico")
    diagnosis_code: Optional[str] = Field(None, description="Código CIE-10")
    diagnosis_description: Optional[str] = Field(None, description="Descripción del diagnóstico")
    observations: Optional[str] = Field(None, description="Observaciones y tratamiento")
    laboratory_tests: Optional[str] = Field(None, description="Exámenes solicitados")
    temperature: Optional[str] = Field(None, description="Temperatura corporal")
    blood_pressure: Optional[str] = Field(None, description="Presión arterial")
    heart_rate: Optional[str] = Field(None, description="Frecuencia cardíaca")
    oxygen_saturation: Optional[str] = Field(None, description="Saturación de oxígeno")
    weight: Optional[str] = Field(None, description="Peso")
    height: Optional[str] = Field(None, description="Talla")




class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    patient_id: Optional[int] = Field(None, description="ID del paciente")
    appointment_date: Optional[date] = Field(None, description="Fecha de la cita")
    appointment_time: Optional[time] = Field(None, description="Hora de la cita")
    current_illness: Optional[str] = Field(None, description="Enfermedad actual")
    physical_examination: Optional[str] = Field(None, description="Examen físico")
    diagnosis_code: Optional[str] = Field(None, description="Código CIE-10")
    diagnosis_description: Optional[str] = Field(None, description="Descripción del diagnóstico")
    observations: Optional[str] = Field(None, description="Observaciones y tratamiento")
    laboratory_tests: Optional[str] = Field(None, description="Exámenes solicitados")
    temperature: Optional[str] = Field(None, description="Temperatura corporal")
    blood_pressure: Optional[str] = Field(None, description="Presión arterial")
    heart_rate: Optional[str] = Field(None, description="Frecuencia cardíaca")
    oxygen_saturation: Optional[str] = Field(None, description="Saturación de oxígeno")
    weight: Optional[str] = Field(None, description="Peso")
    height: Optional[str] = Field(None, description="Talla")



class PatientBasic(BaseModel):
    id: int
    first_name: str
    last_name: str
    document_id: str
    medical_history: Optional[str] = None

    class Config:
        from_attributes = True


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    appointment_date: date
    appointment_time: time
    current_illness: Optional[str] = None
    physical_examination: Optional[str] = None
    diagnosis_code: Optional[str] = None
    diagnosis_description: Optional[str] = None
    observations: Optional[str] = None
    laboratory_tests: Optional[str] = None
    temperature: Optional[str] = None
    blood_pressure: Optional[str] = None
    heart_rate: Optional[str] = None
    oxygen_saturation: Optional[str] = None
    weight: Optional[str] = None
    height: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    patient: Optional[PatientBasic] = None

    class Config:
        from_attributes = True


class AppointmentWithPatientDetails(AppointmentResponse):
    # Campos adicionales para la vista completa
    vital_signs: Optional[VitalSigns] = None
    diagnosis: Optional[DiagnosisInfo] = None

    @validator('vital_signs', pre=True, always=True)
    def build_vital_signs(cls, v, values):
        return VitalSigns(
            temperature=values.get('temperature'),
            blood_pressure=values.get('blood_pressure'),
            heart_rate=values.get('heart_rate'),
            oxygen_saturation=values.get('oxygen_saturation'),
            weight=values.get('weight'),
            height=values.get('height')
        )

    @validator('diagnosis', pre=True, always=True)
    def build_diagnosis(cls, v, values):
        return DiagnosisInfo(
            code=values.get('diagnosis_code'),
            description=values.get('diagnosis_description')
        )