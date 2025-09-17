from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from database.db import get_db
from schemas.patient import PatientCreate, PatientUpdate, PatientResponse
from schemas.report import ReportResponse
from services import patient_service, report_service
from typing import List


router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/recipe/{appointment_id}", response_model=ReportResponse)
def generate_recipe_report(
        appointment_id: int,
        background_tasks: BackgroundTasks,
        db_host: str = Query("localhost", description="Host de la base de datos"),
        db_port: str = Query("5432", description="Puerto de la base de datos"),
        db_name: str = Query("femixweb3", description="Nombre de la base de datos"),
        db_user: str = Query("postgres", description="Usuario de la base de datos"),
        db_password: str = Query("sa", description="Contraseña de la base de datos"),
        db: Session = Depends(get_db)
):
    """
    Generar reporte de receta médica para una cita específica

    Args:
        appointment_id: ID de la cita médica
        background_tasks: Tareas en segundo plano
        db_host: Host de la base de datos
        db_port: Puerto de la base de datos
        db_name: Nombre de la base de datos
        db_user: Usuario de la base de datos
        db_password: Contraseña de la base de datos
        db: Sesión de base de datos

    Returns:
        Información del reporte generado
    """
    try:


        # Generar el reporte
        report_data = report_service.generate_recipe_report(
            appointment_id=appointment_id,
            db_host=db_host,
            db_port=db_port,
            db_name=db_name,
            db_user=db_user,
            db_password=db_password
        )

        # Programar limpieza del archivo temporal en segundo plano
        background_tasks.add_task(
            report_service.cleanup_temp_file,
            report_data["file_path"],
            delay_minutes=30
        )

        return report_data

    except Exception as e:
        print(f"Error generando reporte para cita {appointment_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recipe report: {str(e)}"
        )