from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from models.Appointment import Appointment
from models.Patient import Patient
from schemas.appointment import AppointmentCreate, AppointmentUpdate
from typing import List, Optional
from datetime import date, datetime, timedelta
from fastapi import HTTPException, status


def create_appointment(db: Session, appointment_data: AppointmentCreate) -> Appointment:
    """Crear una nueva cita médica"""

    # Verificar que el paciente existe
    patient = db.query(Patient).filter(Patient.id == appointment_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con ID {appointment_data.patient_id} no encontrado"
        )

    # Verificar disponibilidad de fecha y hora
    existing_appointment = db.query(Appointment).filter(
        and_(
            Appointment.appointment_date == appointment_data.appointment_date,
            Appointment.appointment_time == appointment_data.appointment_time
        )
    ).first()

    if existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una cita programada para {appointment_data.appointment_date} a las {appointment_data.appointment_time}"
        )

    # Crear la nueva cita
    db_appointment = Appointment(**appointment_data.model_dump())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)

    return db_appointment


def get_appointments(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        include_patient: bool = True
) -> List[Appointment]:
    """Obtener lista de citas con paginación"""
    query = db.query(Appointment)

    if include_patient:
        query = query.options(joinedload(Appointment.patient))

    return query.order_by(desc(Appointment.appointment_date), desc(Appointment.appointment_time)).offset(skip).limit(
        limit).all()


def get_appointment_by_id(db: Session, appointment_id: int) -> Optional[Appointment]:
    """Obtener cita por ID"""
    return (db.query(Appointment)
            .options(joinedload(Appointment.patient))
            .filter(Appointment.id == appointment_id).first())


def get_appointments_by_patient(
        db: Session,
        patient_id: int,
        skip: int = 0,
        limit: int = 100
) -> List[Appointment]:
    """Obtener citas de un paciente específico"""
    return (db.query(Appointment)
            .options(joinedload(Appointment.patient))
            .filter(Appointment.patient_id == patient_id)
            .order_by(desc(Appointment.appointment_date), desc(Appointment.appointment_time))
            .offset(skip).limit(limit).all())


def get_appointments_by_date_range(
        db: Session,
        start_date: date,
        end_date: date,
        skip: int = 0,
        limit: int = 100
) -> List[Appointment]:
    """Obtener citas en un rango de fechas"""
    return (db.query(Appointment)
            .options(joinedload(Appointment.patient))
            .filter(
        and_(
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        )
    )
            .order_by(asc(Appointment.appointment_date), asc(Appointment.appointment_time))
            .offset(skip).limit(limit).all())


def search_appointments(
        db: Session,
        query: str,
        skip: int = 0,
        limit: int = 100
) -> List[Appointment]:
    """Buscar citas por nombre, apellido o cédula del paciente"""
    # Preparar el término de búsqueda para LIKE
    search_term = f"%{query.lower()}%"

    return (db.query(Appointment)
            .options(joinedload(Appointment.patient))
            .join(Patient)
            .filter(
        or_(
            func.lower(Patient.first_name).like(search_term),
            func.lower(Patient.last_name).like(search_term),
            Patient.document_id.contains(query),
            func.lower(Appointment.diagnosis_description).like(search_term)
        )
    )
            .order_by(desc(Appointment.appointment_date), desc(Appointment.appointment_time))
            .offset(skip).limit(limit).all())


def update_appointment(
        db: Session,
        appointment_id: int,
        appointment_data: AppointmentUpdate
) -> Optional[Appointment]:
    """Actualizar una cita existente"""
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cita con ID {appointment_id} no encontrada"
        )

    # Si se está actualizando la fecha/hora, verificar disponibilidad
    if appointment_data.appointment_date and appointment_data.appointment_time:
        existing_appointment = db.query(Appointment).filter(
            and_(
                Appointment.id != appointment_id,
                Appointment.appointment_date == appointment_data.appointment_date,
                Appointment.appointment_time == appointment_data.appointment_time
            )
        ).first()

        if existing_appointment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe otra cita programada para {appointment_data.appointment_date} a las {appointment_data.appointment_time}"
            )

    # Actualizar solo los campos proporcionados
    update_data = appointment_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_appointment, field, value)

    db_appointment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_appointment)

    return db_appointment


def delete_appointment(db: Session, appointment_id: int) -> bool:
    """Eliminar una cita"""
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cita con ID {appointment_id} no encontrada"
        )

    db.delete(db_appointment)
    db.commit()
    return True


def get_today_appointments(db: Session) -> List[Appointment]:
    """Obtener las citas del día actual"""
    try:
        today = date.today()
        appointments = (db.query(Appointment)
                        .options(joinedload(Appointment.patient))
                        .filter(Appointment.appointment_date == today)
                        .order_by(asc(Appointment.appointment_time)).all())
        return appointments
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las citas del día actual: {str(e)}"
        )


def get_appointment_count_by_patient(db: Session, patient_id: int) -> int:
    """Contar el número total de citas de un paciente"""
    return (db.query(Appointment)
            .filter(Appointment.patient_id == patient_id).count())


def get_upcoming_appointments(
        db: Session,
        days_ahead: int = 7,
        skip: int = 0,
        limit: int = 100
) -> List[Appointment]:
    """Obtener citas próximas en los próximos N días"""
    today = date.today()
    future_date = today + timedelta(days=days_ahead)

    return (db.query(Appointment)
            .options(joinedload(Appointment.patient))
            .filter(
        and_(
            Appointment.appointment_date >= today,
            Appointment.appointment_date <= future_date
        )
    )
            .order_by(asc(Appointment.appointment_date), asc(Appointment.appointment_time))
            .offset(skip).limit(limit).all())


def get_appointments_by_status(
        db: Session,
        status_filter: str,
        skip: int = 0,
        limit: int = 100
) -> List[Appointment]:
    """Obtener citas por estado (si el modelo tiene campo status)"""
    return (db.query(Appointment)
            .options(joinedload(Appointment.patient))
            .filter(Appointment.status == status_filter)
            .order_by(desc(Appointment.appointment_date), desc(Appointment.appointment_time))
            .offset(skip).limit(limit).all())