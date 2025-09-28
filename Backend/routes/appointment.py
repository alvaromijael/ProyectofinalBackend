from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

# Importaciones de tus servicios y esquemas
from services.appointment_service import (
    create_appointment,
    get_appointments,
    get_appointment_by_id,
    search_appointments,
    update_appointment,
    manage_appointment,
    delete_appointment,
    get_today_appointments,
    get_appointment_count_by_patient, get_appointments_by_user,
)
from schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse, AppointmentManage
from database.db import get_db

router = APIRouter(prefix="/appointments", tags=["appointments"])



@router.get("/search", response_model=List[AppointmentResponse])
def search_appointments_endpoint(
        db: Session = Depends(get_db),
        query: str = Query(default="", description="Buscar por nombre, apellido o cédula del paciente"),
        start_date: Optional[date] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
        end_date: Optional[date] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
        skip: int = Query(0, ge=0, description="Número de registros a omitir"),
        limit: int = Query(100, ge=1, le=1000, description="Límite de registros")
):
    """
    Buscar citas médicas con múltiples criterios:
    - Por nombre, apellido o cédula del paciente
    - Por rango de fechas
    - Combinación de ambos criterios

    Ejemplos de uso:
    - `/appointments/search?query=Juan` - Busca pacientes con nombre Juan
    - `/appointments/search?start_date=2024-01-01&end_date=2024-01-31` - Citas de enero 2024
    - `/appointments/search?query=12345&start_date=2024-01-01` - Paciente con cédula 12345 desde enero
    """

    try:
        # Convertir string vacío a None para la lógica de búsqueda
        search_query = query.strip() if query.strip() else None

        # Validar que al menos un criterio de búsqueda esté presente
        if not search_query and not start_date and not end_date:
            raise HTTPException(
                status_code=400,
                detail="Debe proporcionar al menos un criterio de búsqueda: query, start_date o end_date"
            )

        appointments = search_appointments(
            db=db,
            query=search_query,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )

        return appointments

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al buscar citas"
        )

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




@router.get("/search", response_model=List[AppointmentResponse])
def search_appointments_route(
    q: str = Query(..., min_length=1, description="Término de búsqueda"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Buscar citas por nombre, apellido o cédula del paciente"""
    return search_appointments(db, q, skip, limit)











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

@router.put("/{appointment_id}", response_model=AppointmentResponse)
def manage_appointment_route(
    appointment_id: int,
    appointment_data: AppointmentManage,
    db: Session = Depends(get_db)
):
    """Gestionar una cita existente"""
    return manage_appointment(db, appointment_id, appointment_data)


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


@router.get("/user/{user_id}", response_model=List[AppointmentResponse])
def get_user_appointments(
        user_id: int,
        db: Session = Depends(get_db),
        query: Optional[str] = Query(None,
                                     description="Buscar por nombre, apellido, cédula del paciente o diagnóstico"),
        start_date: Optional[date] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
        end_date: Optional[date] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
        skip: int = Query(0, ge=0, description="Número de registros a omitir"),
        limit: int = Query(100, ge=1, le=500, description="Número máximo de registros a retornar"),
        include_patient: bool = Query(True, description="Incluir información del paciente"),
        include_recipes: bool = Query(True, description="Incluir recetas médicas"),
        include_diagnoses: bool = Query(True, description="Incluir diagnósticos")
):
    """
    Obtener todas las citas de un médico específico con filtros opcionales.

    Filtros disponibles:
    - query: Búsqueda por texto en nombre, apellido, cédula del paciente o diagnóstico
    - start_date: Filtrar citas desde esta fecha
    - end_date: Filtrar citas hasta esta fecha
    - Paginación con skip y limit
    """
    try:
        appointments = get_appointments_by_user(
            db=db,
            user_id=user_id,
            query=query,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit,
            include_patient=include_patient,
            include_recipes=include_recipes,
            include_diagnoses=include_diagnoses
        )
        return appointments
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener las citas del médico: {str(e)}"
        )

