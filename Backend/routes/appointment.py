from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

# Importaciones de tus servicios y esquemas
from services.appointment_service import (
    create_appointment,
    get_appointments,
    get_appointment_by_id,
    get_appointments_by_patient,
    get_appointments_by_date_range,
    search_appointments,
    update_appointment,
    delete_appointment,
    get_today_appointments,
    get_appointment_count_by_patient,
    get_upcoming_appointments,
    get_appointments_by_status
)
from schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from database.db import get_db

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("/", response_model=AppointmentResponse, status_code=201)
def create_new_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db)
):
    """Crear una nueva cita médica"""
    return create_appointment(db, appointment_data)


@router.get("/", response_model=List[AppointmentResponse])
def get_all_appointments(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de registros a retornar"),
    include_patient: bool = Query(True, description="Incluir información del paciente"),
    db: Session = Depends(get_db)
):
    """Obtener lista de citas con paginación"""
    return get_appointments(db, skip, limit, include_patient)


@router.get("/today", response_model=List[AppointmentResponse])
def get_today_appointments_route(db: Session = Depends(get_db)):
    """Obtener las citas del día actual"""
    return get_today_appointments(db)


@router.get("/upcoming", response_model=List[AppointmentResponse])
def get_upcoming_appointments_route(
    days_ahead: int = Query(7, ge=1, le=365, description="Días hacia adelante"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Obtener citas próximas en los próximos N días"""
    return get_upcoming_appointments(db, days_ahead, skip, limit)


@router.get("/search", response_model=List[AppointmentResponse])
def search_appointments_route(
    q: str = Query(..., min_length=1, description="Término de búsqueda"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Buscar citas por nombre, apellido o cédula del paciente"""
    return search_appointments(db, q, skip, limit)


@router.get("/by-date-range", response_model=List[AppointmentResponse])
def get_appointments_by_date_range_route(
    start_date: date = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Fecha de fin (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Obtener citas en un rango de fechas"""
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="La fecha de inicio debe ser anterior o igual a la fecha de fin"
        )
    return get_appointments_by_date_range(db, start_date, end_date, skip, limit)


@router.get("/by-status/{status_filter}", response_model=List[AppointmentResponse])
def get_appointments_by_status_route(
    status_filter: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Obtener citas por estado"""
    return get_appointments_by_status(db, status_filter, skip, limit)


@router.get("/patient/{patient_id}", response_model=List[AppointmentResponse])
def get_appointments_by_patient_route(
    patient_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Obtener citas de un paciente específico"""
    return get_appointments_by_patient(db, patient_id, skip, limit)


@router.get("/patient/{patient_id}/count")
def get_appointment_count_by_patient_route(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """Contar el número total de citas de un paciente"""
    count = get_appointment_count_by_patient(db, patient_id)
    return {"patient_id": patient_id, "appointment_count": count}


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment_by_id_route(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Obtener cita por ID"""
    appointment = get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail=f"Cita con ID {appointment_id} no encontrada"
        )
    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment_route(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar una cita existente"""
    return update_appointment(db, appointment_id, appointment_data)


@router.delete("/{appointment_id}")
def delete_appointment_route(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar una cita"""
    success = delete_appointment(db, appointment_id)
    if success:
        return {"message": f"Cita con ID {appointment_id} eliminada exitosamente"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Error interno al eliminar la cita"
        )