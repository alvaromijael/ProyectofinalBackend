from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
import datetime


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: Optional[EmailStr] = None
    document_id: Optional[str] = None
    relationship_type: str


class ContactCreate(ContactBase):
    pass


class ContactResponse(ContactBase):
    id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True


# ----------------- Paciente -----------------
class PatientBase(BaseModel):
    first_name: str
    last_name: str
    gender: str
    document_id: str
    medical_history: Optional[str] = None

    birth_date: Optional[datetime.date] = None
    marital_status: Optional[str] = None
    occupation: Optional[str] = None
    education: Optional[str] = None
    origin: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    neighborhood: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    notes: Optional[str] = None
    enterprise : Optional[str] = None
    work_activity : Optional[str] = None


class PatientCreate(BaseModel):
    # Campos obligatorios
    first_name: str
    last_name: str
    birth_date: datetime.date
    gender: str
    document_id: str

    # Campos opcionales
    medical_history: Optional[str] = None
    marital_status: Optional[str] = None
    occupation: Optional[str] = None
    education: Optional[str] = None
    origin: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    neighborhood: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    notes: Optional[str] = None
    enterprise: Optional[str] = None
    work_activity: Optional[str] = None
    contacts: List[ContactCreate] = Field(default_factory=list)


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[datetime.date] = None
    gender: Optional[str] = None
    document_id: Optional[str] = None
    marital_status: Optional[str] = None
    occupation: Optional[str] = None
    education: Optional[str] = None
    origin: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    neighborhood: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    medical_history: Optional[str] = None
    notes: Optional[str] = None
    enterprise: Optional[str] = None
    work_activity: Optional[str] = None
    contacts: Optional[List[ContactCreate]] = Field(default_factory=list)


class PatientResponse(PatientBase):
    id: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    contacts: Optional[List[ContactResponse]] = Field(default_factory=list)
    document_id: Optional[str] = None

    class Config:
        orm_mode = True


class PatientManage(BaseModel):
    first_name: str
    last_name: str
    birth_date: datetime.date
    gender: str
    document_id: str
    medical_history: Optional[str] = None
    marital_status: Optional[str] = None
    occupation: Optional[str] = None
    education: Optional[str] = None
    origin: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    neighborhood: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    notes: Optional[str] = None
    enterprise: Optional[str] = None
    work_activity: Optional[str] = None
    contacts: List[ContactCreate] = Field(default_factory=list)
