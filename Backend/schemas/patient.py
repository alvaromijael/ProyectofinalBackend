from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
import datetime

# ----------------- Contactos -----------------
class ContactBase(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: Optional[EmailStr] = None
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
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[datetime.date] = None
    age: Optional[str] = None
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

class PatientCreate(PatientBase):
    contacts: List[ContactCreate] = Field(default_factory=list)

class PatientUpdate(PatientBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[datetime.date] = None
    age: Optional[str] = None
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
    contacts: Optional[List[ContactCreate]] = Field(default_factory=list)  # ✅ mutable default seguro

class PatientResponse(PatientBase):
    id: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    contacts: Optional[List[ContactResponse]] = Field(default_factory=list)

    class Config:
        orm_mode = True
