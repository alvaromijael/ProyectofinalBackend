# contact_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from models.Contact import Contact
from schemas.patient import ContactResponse

logger = logging.getLogger(__name__)


def get_contacts_by_patient_id(db: Session, patient_id: int) -> List[ContactResponse]:
    """Obtener todos los contactos de un paciente por su ID"""
    try:
        contacts = db.query(Contact).filter(Contact.patient_id == patient_id).all()

        if not contacts:
            logger.info(f"No se encontraron contactos para el paciente con ID {patient_id}")
            return []

        logger.info(f"✅ Encontrados {len(contacts)} contactos para el paciente {patient_id}")
        return [ContactResponse.model_validate(contact, from_attributes=True) for contact in contacts]

    except Exception as e:
        logger.error(f"Error al obtener contactos del paciente {patient_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener los contactos del paciente"
        )