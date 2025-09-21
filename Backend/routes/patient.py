from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.db import get_db
from schemas.patient import PatientCreate, PatientUpdate, PatientResponse, PatientManage
from services import patient_service
from typing import List

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("/search", response_model=List[PatientResponse])
def search_patients(
        query: str = Query(..., min_length=3, max_length=100,
                           description="Término de búsqueda (nombres, apellidos o cédula)"),
        skip: int = Query(0, ge=0, description="Número de registros a saltar"),
        limit: int = Query(100, ge=1, le=1000, description="Límite de registros a devolver"),
        db: Session = Depends(get_db)
):

    return patient_service.search_patients(db, query, skip, limit)

@router.post("/", response_model=PatientResponse)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    return patient_service.create_patient(db, patient)

@router.get("/", response_model=List[PatientResponse])
def list_patients(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return patient_service.get_patients(db, skip, limit)

@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = patient_service.get_patient(db, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, patient: PatientUpdate, db: Session = Depends(get_db)):
    db_patient = patient_service.update_patient(db, patient_id, patient)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient


@router.put("/manage/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, patient: PatientManage, db: Session = Depends(get_db)):
    db_patient = patient_service.manage_patient(db, patient_id, patient)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@router.delete("/{patient_id}", status_code=204)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    deleted_patient = patient_service.delete_patient(db, patient_id)
    if not deleted_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return None  # No devuelve contenido


