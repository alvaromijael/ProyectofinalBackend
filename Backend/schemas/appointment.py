from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, time, datetime
from decimal import Decimal


class RecipeBase(BaseModel):
    medicine: str = Field(..., description="Nombre del medicamento")
    amount: str = Field(..., description="Cantidad/dosis del medicamento")
    instructions: str = Field(..., description="Instrucciones de uso")
    lunchTime: str = Field(None, description="Horario de Almuerzo")
    observations: Optional[str] = Field(None, description="Observaciones adicionales")


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(BaseModel):
    medicine: Optional[str] = Field(None, description="Nombre del medicamento")
    amount: Optional[str] = Field(None, description="Cantidad/dosis del medicamento")
    instructions: Optional[str] = Field(None, description="Instrucciones de uso")
    lunchTime: str = Field(None, description="Horario de Almuerzo")
    observations: Optional[str] = Field(None, description="Observaciones adicionales")


class RecipeResponse(BaseModel):
    id: int
    appointment_id: int
    medicine: str
    amount: str
    instructions: str
    lunchTime: Optional[str] = None
    observations: Optional[str] = None

    class Config:
        from_attributes = True


class DiagnosisBase(BaseModel):
    diagnosis_code: str = Field(..., description="Código CIE-10")
    diagnosis_description: str = Field(..., description="Descripción del diagnóstico")
    diagnosis_type: Optional[str] = Field("secondary", description="Tipo de diagnóstico (primary/secondary)")


class DiagnosisCreate(DiagnosisBase):
    pass


class DiagnosisUpdate(BaseModel):
    diagnosis_code: Optional[str] = Field(None, description="Código CIE-10")
    diagnosis_description: Optional[str] = Field(None, description="Descripción del diagnóstico")
    diagnosis_type: Optional[str] = Field(None, description="Tipo de diagnóstico (primary/secondary)")


class DiagnosisResponse(BaseModel):
    id: int
    appointment_id: int
    diagnosis_code: str
    diagnosis_description: str
    diagnosis_type: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class VitalSigns(BaseModel):
    temperature: Optional[str] = Field(None, description="Temperatura corporal en °C")
    blood_pressure: Optional[str] = Field(None, description="Presión arterial (ej: 120/80)")
    heart_rate: Optional[str] = Field(None, description="Frecuencia cardíaca en lpm")
    oxygen_saturation: Optional[str] = Field(None, description="Saturación de oxígeno en %")
    weight: Optional[Decimal] = Field(None, description="Peso (valor numérico)")
    weight_unit: Optional[str] = Field("kg", description="Unidad de peso (kg, lb, g)")
    height: Optional[str] = Field(None, description="Talla en cm")


class AppointmentBase(BaseModel):
    patient_id: int = Field(..., description="ID del paciente")
    appointment_date: date = Field(..., description="Fecha de la cita")
    appointment_time: time = Field(..., description="Hora de la cita")
    current_illness: Optional[str] = Field(None, description="Enfermedad actual")
    physical_examination: Optional[str] = Field(None, description="Examen físico")
    observations: Optional[str] = Field(None, description="Observaciones y tratamiento")
    laboratory_tests: Optional[str] = Field(None, description="Exámenes solicitados")
    temperature: Optional[str] = Field(None, description="Temperatura corporal")
    blood_pressure: Optional[str] = Field(None, description="Presión arterial")
    heart_rate: Optional[str] = Field(None, description="Frecuencia cardíaca")
    oxygen_saturation: Optional[str] = Field(None, description="Saturación de oxígeno")
    weight: Optional[Decimal] = Field(None, description="Peso (valor numérico)")
    weight_unit: Optional[str] = Field("kg", description="Unidad de peso (kg, lb, g)")
    height: Optional[str] = Field(None, description="Talla")
    medical_preinscription: Optional[str] = Field(None, description="Prescripción Médica")


class AppointmentCreate(AppointmentBase):
    diagnoses: Optional[List[DiagnosisCreate]] = Field(default_factory=list, description="Lista de diagnósticos")
    recipes: Optional[List[RecipeCreate]] = Field(default_factory=list, description="Lista de recetas médicas")


class AppointmentUpdate(BaseModel):
    patient_id: Optional[int] = Field(None, description="ID del paciente")
    appointment_date: Optional[date] = Field(None, description="Fecha de la cita")
    appointment_time: Optional[time] = Field(None, description="Hora de la cita")
    current_illness: Optional[str] = Field(None, description="Enfermedad actual")
    physical_examination: Optional[str] = Field(None, description="Examen físico")
    observations: Optional[str] = Field(None, description="Observaciones y tratamiento")
    laboratory_tests: Optional[str] = Field(None, description="Exámenes solicitados")
    temperature: Optional[str] = Field(None, description="Temperatura corporal")
    blood_pressure: Optional[str] = Field(None, description="Presión arterial")
    heart_rate: Optional[str] = Field(None, description="Frecuencia cardíaca")
    oxygen_saturation: Optional[str] = Field(None, description="Saturación de oxígeno")
    weight: Optional[Decimal] = Field(None, description="Peso (valor numérico)")
    weight_unit: Optional[str] = Field(None, description="Unidad de peso (kg, lb, g)")
    height: Optional[str] = Field(None, description="Talla")
    medical_preinscription: Optional[str] = Field(None, description="Prescripción Médica")
    diagnoses: Optional[List[DiagnosisUpdate]] = Field(None, description="Lista de diagnósticos")
    recipes: Optional[List[RecipeUpdate]] = Field(None, description="Lista de recetas médicas")


# 🔧 ESQUEMA CORREGIDO: AppointmentManage
class AppointmentManage(BaseModel):
    # Campos opcionales para flexibilidad en la gestión médica
    current_illness: Optional[str] = Field(None, description="Enfermedad actual")
    physical_examination: Optional[str] = Field(None, description="Examen físico")
    observations: Optional[str] = Field(None, description="Observaciones y tratamiento")
    laboratory_tests: Optional[str] = Field(None, description="Exámenes solicitados")

    # Signos vitales (opcionales)
    temperature: Optional[str] = Field(None, description="Temperatura corporal")
    blood_pressure: Optional[str] = Field(None, description="Presión arterial")
    heart_rate: Optional[str] = Field(None, description="Frecuencia cardíaca")
    oxygen_saturation: Optional[str] = Field(None, description="Saturación de oxígeno")
    weight: Optional[Decimal] = Field(None, description="Peso (valor numérico)")
    weight_unit: Optional[str] = Field("kg", description="Unidad de peso (kg, lb, g)")
    height: Optional[str] = Field(None, description="Talla")

    # 🎯 CAMPO PRINCIPAL: Prescripción médica
    medical_preinscription: Optional[str] = Field(None, description="Prescripción Médica")

    # Diagnósticos y recetas (opcionales para flexibilidad)
    diagnoses: Optional[List[DiagnosisUpdate]] = Field(default_factory=list, description="Lista de diagnósticos")
    recipes: Optional[List[RecipeUpdate]] = Field(default_factory=list, description="Lista de recetas médicas")

    class Config:
        # Configuración para mejor validación
        validate_assignment = True
        str_strip_whitespace = True


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
    observations: Optional[str] = None
    laboratory_tests: Optional[str] = None
    temperature: Optional[str] = None
    blood_pressure: Optional[str] = None
    heart_rate: Optional[str] = None
    oxygen_saturation: Optional[str] = None
    weight: Optional[Decimal] = None
    weight_unit: Optional[str] = "kg"
    height: Optional[str] = None
    medical_preinscription: Optional[str] = Field(None, description="Prescripción Médica")
    created_at: datetime
    updated_at: Optional[datetime] = None
    patient: Optional[PatientBasic] = None
    diagnoses: Optional[List[DiagnosisResponse]] = Field(default_factory=list, description="Lista de diagnósticos")
    recipes: Optional[List[RecipeResponse]] = Field(default_factory=list, description="Lista de recetas médicas")

    class Config:
        from_attributes = True


class AppointmentWithPatientDetails(AppointmentResponse):
    # Campos adicionales para la vista completa
    vital_signs: Optional[VitalSigns] = None

    @validator('vital_signs', pre=True, always=True)
    def build_vital_signs(cls, v, values):
        return VitalSigns(
            temperature=values.get('temperature'),
            blood_pressure=values.get('blood_pressure'),
            heart_rate=values.get('heart_rate'),
            oxygen_saturation=values.get('oxygen_saturation'),
            weight=values.get('weight'),
            weight_unit=values.get('weight_unit', 'kg'),
            height=values.get('height')
        )