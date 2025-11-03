# patient_service.py - CRUD completo para Patient
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
import logging

from models.Patient import Patient
from models.Contact import Contact
from schemas.patient import PatientCreate, PatientUpdate, PatientResponse, ContactResponse, PatientManage

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

        # ✅ ACTUALIZAR CONTACTOS PRESERVANDO REFERENCIAS
        if hasattr(patient_update, 'contacts') and patient_update.contacts is not None:
            print(f"\n{'=' * 60}")
            print(f"🔍 INICIANDO ACTUALIZACIÓN DE CONTACTOS")
            print(f"{'=' * 60}")

            # Ver qué contactos vienen en el request
            contacts_received = [c.model_dump() for c in patient_update.contacts]
            print(f"🔍 Contactos recibidos del frontend:")
            for c in contacts_received:
                print(f"   - ID: {c.get('id')} | Nombre: {c.get('first_name')} {c.get('last_name')}")

            # Obtener contactos existentes EN LA BASE DE DATOS
            existing_contacts = db.query(Contact).filter(Contact.patient_id == patient_id).all()
            existing_contacts_dict = {contact.id: contact for contact in existing_contacts}

            print(f"\n🔍 Contactos existentes en BD para paciente {patient_id}:")
            if existing_contacts_dict:
                for contact_id, contact in existing_contacts_dict.items():
                    print(f"   - ID: {contact_id} | Nombre: {contact.first_name} {contact.last_name}")
            else:
                print(f"   ❌ NO HAY CONTACTOS EN LA BD PARA ESTE PACIENTE")

            # IDs que vienen en el update
            incoming_ids = set()

            print(f"\n{'=' * 60}")
            print(f"🔍 PROCESANDO CADA CONTACTO")
            print(f"{'=' * 60}")

            for contact_data in patient_update.contacts:
                contact_dict = contact_data.model_dump()
                contact_id = contact_dict.get('id')

                print(f"\n📋 Contacto: {contact_dict.get('first_name')} {contact_dict.get('last_name')}")
                print(f"   ID recibido: {contact_id}")
                print(f"   ¿Existe en BD?: {contact_id in existing_contacts_dict if contact_id else False}")

                if contact_id and contact_id in existing_contacts_dict:
                    # ✅ ACTUALIZAR contacto existente
                    incoming_ids.add(contact_id)
                    db_contact = existing_contacts_dict[contact_id]

                    print(f"   ✏️  ACTUALIZANDO contacto existente ID: {contact_id}")
                    for field, value in contact_dict.items():
                        if field != 'id':
                            old_value = getattr(db_contact, field, None)
                            if old_value != value:
                                setattr(db_contact, field, value)
                                print(f"      {field}: {old_value} → {value}")
                else:
                    # ➕ CREAR nuevo contacto
                    print(f"   ➕ CREANDO NUEVO contacto")
                    if contact_id:
                        print(f"      ⚠️  Se envió ID {contact_id} pero NO existe en BD")

                    new_contact = Contact(
                        **{k: v for k, v in contact_dict.items() if k != 'id'},
                        patient_id=patient_id
                    )
                    db.add(new_contact)

            print(f"\n{'=' * 60}")
            print(f"🔍 IDs que deben permanecer: {incoming_ids}")
            print(f"🔍 IDs en BD actualmente: {set(existing_contacts_dict.keys())}")
            print(f"{'=' * 60}")

            # 🗑️ ELIMINAR contactos que ya no están en la lista
            ids_to_delete = set(existing_contacts_dict.keys()) - incoming_ids
            if ids_to_delete:
                print(f"\n🗑️  ELIMINANDO contactos: {ids_to_delete}")
                for contact_id in ids_to_delete:
                    contact = existing_contacts_dict[contact_id]
                    print(f"   Eliminando ID: {contact_id} | {contact.first_name} {contact.last_name}")
                    db.delete(contact)
            else:
                print(f"\n✅ No hay contactos para eliminar")

            print(f"\n{'=' * 60}\n")

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


def manage_patient(db: Session, patient_id: int, patient_update: PatientManage) -> PatientResponse:
    """Actualizar un paciente"""
    try:
        db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if db_patient is None:
            raise HTTPException(
                status_code=404,
                detail=f"Paciente con ID {patient_id} no encontrado"
            )

        if not patient_update.medical_history:
            raise HTTPException(
                status_code=400,
                detail="El campo de antecedentes médicos es obligatorio"
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

        # ✅ ACTUALIZAR CONTACTOS PRESERVANDO REFERENCIAS
        if hasattr(patient_update, 'contacts') and patient_update.contacts is not None:
            print(f"\n{'=' * 60}")
            print(f"🔍 INICIANDO ACTUALIZACIÓN DE CONTACTOS")
            print(f"{'=' * 60}")

            # Ver qué contactos vienen en el request
            contacts_received = [c.model_dump() for c in patient_update.contacts]
            print(f"🔍 Contactos recibidos del frontend:")
            for c in contacts_received:
                print(f"   - ID: {c.get('id')} | Nombre: {c.get('first_name')} {c.get('last_name')}")

            # Obtener contactos existentes EN LA BASE DE DATOS
            existing_contacts = db.query(Contact).filter(Contact.patient_id == patient_id).all()
            existing_contacts_dict = {contact.id: contact for contact in existing_contacts}

            print(f"\n🔍 Contactos existentes en BD para paciente {patient_id}:")
            if existing_contacts_dict:
                for contact_id, contact in existing_contacts_dict.items():
                    print(f"   - ID: {contact_id} | Nombre: {contact.first_name} {contact.last_name}")
            else:
                print(f"   ❌ NO HAY CONTACTOS EN LA BD PARA ESTE PACIENTE")

            # IDs que vienen en el update
            incoming_ids = set()

            print(f"\n{'=' * 60}")
            print(f"🔍 PROCESANDO CADA CONTACTO")
            print(f"{'=' * 60}")

            for contact_data in patient_update.contacts:
                contact_dict = contact_data.model_dump()
                contact_id = contact_dict.get('id')

                print(f"\n📋 Contacto: {contact_dict.get('first_name')} {contact_dict.get('last_name')}")
                print(f"   ID recibido: {contact_id}")
                print(f"   ¿Existe en BD?: {contact_id in existing_contacts_dict if contact_id else False}")

                if contact_id and contact_id in existing_contacts_dict:
                    # ✅ ACTUALIZAR contacto existente
                    incoming_ids.add(contact_id)
                    db_contact = existing_contacts_dict[contact_id]

                    print(f"   ✏️  ACTUALIZANDO contacto existente ID: {contact_id}")
                    for field, value in contact_dict.items():
                        if field != 'id':
                            old_value = getattr(db_contact, field, None)
                            if old_value != value:
                                setattr(db_contact, field, value)
                                print(f"      {field}: {old_value} → {value}")
                else:
                    # ➕ CREAR nuevo contacto
                    print(f"   ➕ CREANDO NUEVO contacto")
                    if contact_id:
                        print(f"      ⚠️  Se envió ID {contact_id} pero NO existe en BD")

                    new_contact = Contact(
                        **{k: v for k, v in contact_dict.items() if k != 'id'},
                        patient_id=patient_id
                    )
                    db.add(new_contact)

            print(f"\n{'=' * 60}")
            print(f"🔍 IDs que deben permanecer: {incoming_ids}")
            print(f"🔍 IDs en BD actualmente: {set(existing_contacts_dict.keys())}")
            print(f"{'=' * 60}")

            # 🗑️ ELIMINAR contactos que ya no están en la lista
            ids_to_delete = set(existing_contacts_dict.keys()) - incoming_ids
            if ids_to_delete:
                print(f"\n🗑️  ELIMINANDO contactos: {ids_to_delete}")
                for contact_id in ids_to_delete:
                    contact = existing_contacts_dict[contact_id]
                    print(f"   Eliminando ID: {contact_id} | {contact.first_name} {contact.last_name}")
                    db.delete(contact)
            else:
                print(f"\n✅ No hay contactos para eliminar")

            print(f"\n{'=' * 60}\n")

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

