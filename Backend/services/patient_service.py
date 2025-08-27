# patient_service.py - CRUD completo para Patient
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
import logging

# Ajusta estas importaciones según tu estructura
from models.Patient import Patient
from models.Contact import Contact
from schemas.patient import PatientCreate, PatientUpdate, PatientResponse, ContactResponse




logger = logging.getLogger(__name__)


# CREATE
def create_patient(db: Session, patient: PatientCreate) -> PatientResponse:
    """Crear un nuevo paciente"""
    try:
        # Excluimos los contactos para crear el paciente primero
        patient_data = patient.model_dump(exclude={"contacts"})
        db_patient = Patient(**patient_data)

        # Creamos y asociamos los contactos si existen
        if patient.contacts:
            for contact in patient.contacts:
                db_contact = Contact(**contact.model_dump())
                db_patient.contacts.append(db_contact)

        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)

        return PatientResponse.model_validate(db_patient, from_attributes=True)

    except ValidationError as e:
        logger.error(f"Error de validación al crear PatientResponse: {e}")
        db.rollback()
        raise HTTPException(
            status_code=422,
            detail="Error de validación: No se pudo procesar los datos del paciente"
        )

    except IntegrityError as e:
        logger.error(f"Error de integridad de base de datos: {e}")
        db.rollback()

        error_message = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "document_id" in error_message:
            raise HTTPException(
                status_code=409,
                detail="Ya existe un paciente con este número de documento"
            )
        else:
            raise HTTPException(
                status_code=409,
                detail="Los datos proporcionados violan las restricciones de la base de datos"
            )

    except Exception as e:
        logger.error(f"Error inesperado al crear paciente: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Ha ocurrido un error inesperado al crear el paciente"
        )


# READ - Get all patients
def get_patients(db: Session, skip: int = 0, limit: int = 100) -> List[PatientResponse]:
    """Obtener lista de pacientes con paginación"""
    try:
        patients = db.query(Patient).offset(skip).limit(limit).all()
        return [PatientResponse.model_validate(patient, from_attributes=True) for patient in patients]
    except Exception as e:
        logger.error(f"Error al obtener pacientes: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener la lista de pacientes"
        )


# READ - Get patient by ID
def get_patient(db: Session, patient_id: int) -> PatientResponse:
    """Obtener un paciente por su ID"""
    try:
        db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if db_patient is None:
            raise HTTPException(
                status_code=404,
                detail=f"Paciente con ID {patient_id} no encontrado"
            )
        return PatientResponse.model_validate(db_patient, from_attributes=True)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener paciente {patient_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener el paciente"
        )


# READ - Get patient by document ID
def get_patient_by_document(db: Session, document_id: str) -> Optional[PatientResponse]:
    """Obtener un paciente por su número de documento"""
    try:
        db_patient = db.query(Patient).filter(Patient.document_id == document_id).first()
        if db_patient is None:
            raise HTTPException(
                status_code=404,
                detail=f"Paciente con documento {document_id} no encontrado"
            )
        return PatientResponse.model_validate(db_patient, from_attributes=True)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener paciente por documento {document_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener el paciente"
        )


def search_patients(
        db: Session,
        query: str,
        skip: int = 0,
        limit: int = 100
) -> List[PatientResponse]:
    print("sasasa")
    """Buscar pacientes por nombre, apellido o documento"""
    try:
        # Limpiar el término de búsqueda
        clean_query = query.strip()
        if not clean_query:
            logger.warning("Búsqueda vacía, devolviendo lista vacía")
            return []

        search_term = f"%{clean_query}%"

        logger.info(f"🔍 Buscando pacientes con término: '{clean_query}' (patrón: '{search_term}')")

        # Consulta con campos no nulos para evitar coincidencias falsas
        patients = db.query(Patient).filter(
            or_(
                and_(Patient.first_name.isnot(None), Patient.first_name.ilike(search_term)),
                and_(Patient.last_name.isnot(None), Patient.last_name.ilike(search_term)),
                and_(Patient.document_id.isnot(None), Patient.document_id.ilike(search_term))
            )
        ).offset(skip).limit(limit).all()

        # Debug detallado
        logger.info(f"📊 Encontrados {len(patients)} pacientes:")
        valid_patients = []

        for patient in patients:
            # Doble verificación en Python para asegurar coincidencias válidas
            matched_fields = []
            is_valid_match = False

            if patient.first_name and clean_query.lower() in patient.first_name.lower():
                matched_fields.append(f"nombre: '{patient.first_name}'")
                is_valid_match = True

            if patient.last_name and clean_query.lower() in patient.last_name.lower():
                matched_fields.append(f"apellido: '{patient.last_name}'")
                is_valid_match = True

            if patient.document_id and clean_query.lower() in patient.document_id.lower():
                matched_fields.append(f"cédula: '{patient.document_id}'")
                is_valid_match = True

            if is_valid_match:
                matched_info = " | ".join(matched_fields)
                logger.info(
                    f"   ✅ {patient.last_name}, {patient.first_name} ({patient.document_id}) - Coincide en: {matched_info}")
                valid_patients.append(patient)
            else:
                logger.warning(
                    f"   ❌ FALSA COINCIDENCIA: {patient.last_name}, {patient.first_name} ({patient.document_id}) - Sin coincidencia válida")

        logger.info(f"🎯 Pacientes válidos tras verificación: {len(valid_patients)}")
        return [PatientResponse.model_validate(patient, from_attributes=True) for patient in valid_patients]

    except Exception as e:
        logger.error(f"Error al buscar pacientes: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al buscar pacientes"
        )

def update_patient(db: Session, patient_id: int, patient_update: PatientUpdate) -> PatientResponse:
    """Actualizar un paciente"""
    try:
        db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if db_patient is None:
            raise HTTPException(
                status_code=404,
                detail=f"Paciente con ID {patient_id} no encontrado"
            )

        # DEBUG: Ver qué datos están llegando
        update_data = patient_update.model_dump(exclude_unset=True, exclude={"contacts"})
        print(f"🔍 Datos a actualizar: {update_data}")
        print(f"🔍 Document ID actual: {db_patient.document_id}")
        print(f"🔍 Document ID nuevo: {update_data.get('document_id', 'NO ENVIADO')}")

        # VALIDACIÓN PREVIA: Solo verificar document_id si realmente está cambiando
        if 'document_id' in update_data:
            if update_data['document_id'] != db_patient.document_id:
                print(f"🔍 Document ID está cambiando, validando duplicados...")
                existing_patient = db.query(Patient).filter(
                    Patient.document_id == update_data['document_id']
                ).first()

                if existing_patient:
                    print(f"❌ Documento duplicado encontrado con ID: {existing_patient.id}")
                    raise HTTPException(
                        status_code=409,
                        detail="Ya existe otro paciente con este número de documento"
                    )
            else:
                print(f"✅ Document ID no ha cambiado, no validar duplicados")

        # Actualizar campos del paciente (SOLO si hay cambios reales)
        changes_made = []
        for field, value in update_data.items():
            current_value = getattr(db_patient, field)
            if current_value != value:  # Solo actualizar si hay cambio real
                setattr(db_patient, field, value)
                changes_made.append(f"{field}: {current_value} -> {value}")

        print(f"🔍 Cambios realizados: {changes_made}")

        # Actualizar contactos si se proporcionan
        if hasattr(patient_update, 'contacts') and patient_update.contacts is not None:
            print(f"🔍 Actualizando contactos...")
            # Eliminar contactos existentes
            db.query(Contact).filter(Contact.patient_id == patient_id).delete()

            # Crear nuevos contactos
            for contact_data in patient_update.contacts:
                db_contact = Contact(**contact_data.model_dump(), patient_id=patient_id)
                db.add(db_contact)

        db.commit()
        db.refresh(db_patient)

        return PatientResponse.model_validate(db_patient, from_attributes=True)

    except HTTPException:
        raise
    except IntegrityError as e:
        logger.error(f"Error de integridad al actualizar paciente: {e}")
        db.rollback()

        error_message = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "document_id" in error_message:
            raise HTTPException(
                status_code=409,
                detail="Ya existe otro paciente con este número de documento"
            )
        else:
            raise HTTPException(
                status_code=409,
                detail="Los datos actualizados violan las restricciones de la base de datos"
            )
    except Exception as e:
        logger.error(f"Error inesperado al actualizar paciente: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error inesperado al actualizar el paciente"
        )

# PATCH mejorado también
def patch_patient(db: Session, patient_id: int, patient_patch: dict) -> PatientResponse:
    """Actualización parcial de un paciente"""
    try:
        db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if db_patient is None:
            raise HTTPException(
                status_code=404,
                detail=f"Paciente con ID {patient_id} no encontrado"
            )

        # Si se está actualizando el document_id, verificar que no exista en otro registro
        if 'document_id' in patient_patch:
            existing_patient = db.query(Patient).filter(
                and_(
                    Patient.document_id == patient_patch['document_id'],
                    Patient.id != patient_id  # EXCLUIR el registro actual
                )
            ).first()

            if existing_patient:
                raise HTTPException(
                    status_code=409,
                    detail="Ya existe otro paciente con este número de documento"
                )

        # Actualizar solo los campos proporcionados
        for field, value in patient_patch.items():
            if hasattr(db_patient, field) and field != 'contacts':
                setattr(db_patient, field, value)

        db.commit()
        db.refresh(db_patient)

        return PatientResponse.model_validate(db_patient, from_attributes=True)

    except HTTPException:
        raise
    except IntegrityError as e:
        logger.error(f"Error de integridad al actualizar paciente: {e}")
        db.rollback()

        error_message = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "document_id" in error_message:
            raise HTTPException(
                status_code=409,
                detail="Ya existe otro paciente con este número de documento"
            )
        else:
            raise HTTPException(
                status_code=409,
                detail="Los datos actualizados violan las restricciones de la base de datos"
            )
    except Exception as e:
        logger.error(f"Error inesperado al actualizar paciente: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error inesperado al actualizar el paciente"
        )


# También puedes mejorar tu función utilitaria existente
def check_document_exists(db: Session, document_id: str, exclude_patient_id: Optional[int] = None) -> bool:
    """Verificar si un documento ya existe"""
    try:
        query = db.query(Patient).filter(Patient.document_id == document_id)
        if exclude_patient_id:
            query = query.filter(Patient.id != exclude_patient_id)
        return query.first() is not None
    except Exception as e:
        logger.error(f"Error al verificar documento: {e}")
        return False


# DELETE - Soft delete
def delete_patient(db: Session, patient_id: int) -> dict:
    """Eliminar un paciente (soft delete - marcar como eliminado)"""
    try:
        db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if db_patient is None:
            raise HTTPException(
                status_code=404,
                detail=f"Paciente con ID {patient_id} no encontrado"
            )

        # Si tienes un campo 'is_active' o 'deleted_at' para soft delete
        # db_patient.is_active = False
        # db_patient.deleted_at = datetime.utcnow()

        # Para hard delete (eliminar permanentemente):
        db.delete(db_patient)
        db.commit()

        return {"message": f"Paciente con ID {patient_id} eliminado exitosamente"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar paciente: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error inesperado al eliminar el paciente"
        )


# UTILITY FUNCTIONS
def get_patients_count(db: Session) -> int:
    """Obtener el número total de pacientes"""
    try:
        return db.query(Patient).count()
    except Exception as e:
        logger.error(f"Error al contar pacientes: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener el conteo de pacientes"
        )





def get_patients_by_city(db: Session, city: str, skip: int = 0, limit: int = 100) -> List[PatientResponse]:
    """Obtener pacientes por ciudad"""
    try:
        patients = db.query(Patient).filter(
            Patient.city.ilike(f"%{city}%")
        ).offset(skip).limit(limit).all()

        return [PatientResponse.model_validate(patient, from_attributes=True) for patient in patients]
    except Exception as e:
        logger.error(f"Error al obtener pacientes por ciudad: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener pacientes por ciudad"
        )


def get_patients_by_age_range(
        db: Session,
        min_age: int,
        max_age: int,
        skip: int = 0,
        limit: int = 100
) -> List[PatientResponse]:
    """Obtener pacientes por rango de edad"""
    try:
        patients = db.query(Patient).filter(
            and_(
                Patient.age.cast(db.Integer) >= min_age,
                Patient.age.cast(db.Integer) <= max_age
            )
        ).offset(skip).limit(limit).all()

        return [PatientResponse.model_validate(patient, from_attributes=True) for patient in patients]
    except Exception as e:
        logger.error(f"Error al obtener pacientes por rango de edad: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener pacientes por rango de edad"
        )