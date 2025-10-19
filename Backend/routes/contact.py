# contact_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database.db import get_db
from schemas.patient import ContactResponse
from services.contact_service import get_contacts_by_patient_id

router = APIRouter(
    prefix="/contacts",
    tags=["contacts"]
)


@router.get("/patient/{patient_id}", response_model=List[ContactResponse])
def get_patient_contacts(
        patient_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener todos los contactos de un paciente específico.

    - **patient_id**: ID del paciente

    Retorna una lista de contactos asociados al paciente.
    Útil para seleccionar representantes legales en citas médicas.
    """
    return get_contacts_by_patient_id(db, patient_id)