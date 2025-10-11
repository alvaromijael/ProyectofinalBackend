from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from models.Appointment import Appointment, AppointmentDiagnosis
from models.Patient import Patient
from models.Recipe import Recipe
from schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentManage, AppointmentResponse
from typing import List, Optional
from datetime import date, datetime
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

    # ✅ EXTRAER DIAGNÓSTICOS Y RECETAS ANTES Y REMOVER DEL DICT
    diagnoses_data = appointment_data.diagnoses or []
    recipes_data = appointment_data.recipes or []
    appointment_dict = appointment_data.model_dump()
    appointment_dict.pop('diagnoses', None)  # Remover diagnoses del dict
    appointment_dict.pop('recipes', None)  # Remover recipes del dict

    # Crear la nueva cita SIN las relaciones
    db_appointment = Appointment(**appointment_dict)
    db.add(db_appointment)
    db.flush()  # Para obtener el ID

    # ✅ CREAR LOS DIAGNÓSTICOS POR SEPARADO
    for diagnosis_data in diagnoses_data:
        db_diagnosis = AppointmentDiagnosis(
            appointment_id=db_appointment.id,
            diagnosis_code=diagnosis_data.diagnosis_code,
            diagnosis_description=diagnosis_data.diagnosis_description,
            diagnosis_type=diagnosis_data.diagnosis_type or "secondary"
        )
        db.add(db_diagnosis)

    # ✅ CREAR LAS RECETAS POR SEPARADO
    for recipe_data in recipes_data:
        db_recipe = Recipe(
            appointment_id=db_appointment.id,
            medicine=recipe_data.medicine,
            amount=recipe_data.amount,
            instructions=recipe_data.instructions,
            observations=recipe_data.observations
        )
        db.add(db_recipe)

    db.commit()
    db.refresh(db_appointment)

    return db_appointment


def get_appointments(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        include_patient: bool = True,
        include_recipes: bool = True,
        include_diagnoses: bool = True  # Nuevo parámetro para diagnósticos
) -> List[Appointment]:
    """Obtener lista de citas con paginación"""
    query = db.query(Appointment)

    if include_patient:
        query = query.options(joinedload(Appointment.patient))

    if include_recipes:
        query = query.options(joinedload(Appointment.recipes))

    if include_diagnoses:
        query = query.options(joinedload(Appointment.diagnoses))

    return query.order_by(desc(Appointment.appointment_date), desc(Appointment.appointment_time)).offset(skip).limit(
        limit).all()


def get_appointment_by_id(db: Session, appointment_id: int) -> Optional[AppointmentResponse]:
    """Obtener cita por ID"""
    return (db.query(Appointment)
            .options(
        joinedload(Appointment.patient),
        joinedload(Appointment.recipes),
        joinedload(Appointment.diagnoses)
    )
            .filter(Appointment.id == appointment_id).first())



def search_appointments(
        db: Session,
        query: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
) -> List[Appointment]:
    """
    Buscar citas médicas con múltiples criterios:
    - Por nombre, apellido o cédula del paciente
    - Por rango de fechas
    - Por código o descripción de diagnóstico
    - Combinación de ambos criterios
    """
    # Construir la consulta base
    db_query = db.query(Appointment).options(
        joinedload(Appointment.patient),
        joinedload(Appointment.diagnoses)
    )

    # Lista de condiciones a aplicar
    conditions = []

    # Filtro por texto (nombre, apellido, cédula, diagnóstico)
    if query and query.strip():
        search_term = f"%{query.lower()}%"
        db_query = db_query.join(Patient).outerjoin(AppointmentDiagnosis)
        text_conditions = or_(
            func.lower(Patient.first_name).like(search_term),
            func.lower(Patient.last_name).like(search_term),
            Patient.document_id.contains(query.strip()),
            func.lower(AppointmentDiagnosis.diagnosis_description).like(search_term),
            AppointmentDiagnosis.diagnosis_code.contains(query.strip().upper())
        )
        conditions.append(text_conditions)

    # Filtro por rango de fechas
    if start_date:
        conditions.append(Appointment.appointment_date >= start_date)

    if end_date:
        conditions.append(Appointment.appointment_date <= end_date)

    # Aplicar todas las condiciones
    if conditions:
        db_query = db_query.filter(and_(*conditions))

    # Aplicar ordenamiento y paginación
    return (db_query
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

    # 1. Actualizar campos simples EXCLUYENDO relaciones
    update_data = appointment_data.model_dump(
        exclude_unset=True,
        exclude={'recipes', 'diagnoses'}
    )

    for field, value in update_data.items():
        setattr(db_appointment, field, value)

    # 2. Manejar diagnósticos por separado
    if appointment_data.diagnoses is not None:
        # Eliminar diagnósticos existentes
        db.query(AppointmentDiagnosis).filter(
            AppointmentDiagnosis.appointment_id == appointment_id
        ).delete()

        # Crear nuevos diagnósticos
        for diagnosis_update in appointment_data.diagnoses:
            diagnosis_data = diagnosis_update.model_dump(exclude_unset=True)
            diagnosis_data['appointment_id'] = appointment_id
            new_diagnosis = AppointmentDiagnosis(**diagnosis_data)
            db.add(new_diagnosis)

    # 3. Manejar recipes por separado
    if appointment_data.recipes is not None:
        # Eliminar recetas existentes
        db.query(Recipe).filter(Recipe.appointment_id == appointment_id).delete()

        # Crear nuevas recetas
        for recipe_update in appointment_data.recipes:
            recipe_data = recipe_update.model_dump(exclude_unset=True, exclude={'id'})
            recipe_data['appointment_id'] = appointment_id
            new_recipe = Recipe(**recipe_data)
            db.add(new_recipe)

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
                        .options(
            joinedload(Appointment.patient),
            joinedload(Appointment.diagnoses)
        )
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


# Funciones adicionales para manejo de diagnósticos
def get_diagnoses_by_appointment(db: Session, appointment_id: int) -> List[AppointmentDiagnosis]:
    """Obtener todos los diagnósticos de una cita específica"""
    return (db.query(AppointmentDiagnosis)
            .filter(AppointmentDiagnosis.appointment_id == appointment_id)
            .all())


def add_diagnosis_to_appointment(
        db: Session,
        appointment_id: int,
        diagnosis_code: str,
        diagnosis_description: str,
        diagnosis_type: str = "secondary"
) -> AppointmentDiagnosis:
    """Agregar un diagnóstico a una cita existente"""
    # Verificar que la cita existe
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cita con ID {appointment_id} no encontrada"
        )

    # Crear el nuevo diagnóstico
    new_diagnosis = AppointmentDiagnosis(
        appointment_id=appointment_id,
        diagnosis_code=diagnosis_code,
        diagnosis_description=diagnosis_description,
        diagnosis_type=diagnosis_type
    )

    db.add(new_diagnosis)
    db.commit()
    db.refresh(new_diagnosis)

    return new_diagnosis


def remove_diagnosis_from_appointment(db: Session, diagnosis_id: int) -> bool:
    """Eliminar un diagnóstico específico de una cita"""
    diagnosis = db.query(AppointmentDiagnosis).filter(AppointmentDiagnosis.id == diagnosis_id).first()
    if not diagnosis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diagnóstico con ID {diagnosis_id} no encontrado"
        )

    db.delete(diagnosis)
    db.commit()
    return True



def manage_appointment(
        db: Session,
        appointment_id: int,
        appointment_data: AppointmentManage
) -> Optional[Appointment]:
    print(appointment_data)
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

    # 1. Actualizar campos simples EXCLUYENDO relaciones
    update_data = appointment_data.model_dump(
        exclude_unset=True,
        exclude={'recipes', 'diagnoses'}
    )

    for field, value in update_data.items():
        setattr(db_appointment, field, value)

    # 2. Manejar diagnósticos por separado
    if appointment_data.diagnoses is not None:
        # Eliminar diagnósticos existentes
        db.query(AppointmentDiagnosis).filter(
            AppointmentDiagnosis.appointment_id == appointment_id
        ).delete()

        # Crear nuevos diagnósticos
        for diagnosis_update in appointment_data.diagnoses:
            diagnosis_data = diagnosis_update.model_dump(exclude_unset=True)
            diagnosis_data['appointment_id'] = appointment_id
            new_diagnosis = AppointmentDiagnosis(**diagnosis_data)
            db.add(new_diagnosis)

    # 3. Manejar recipes por separado
    if appointment_data.recipes is not None:
        # Eliminar recetas existentes
        db.query(Recipe).filter(Recipe.appointment_id == appointment_id).delete()

        # Crear nuevas recetas
        for recipe_update in appointment_data.recipes:
            recipe_data = recipe_update.model_dump(exclude_unset=True, exclude={'id'})
            recipe_data['appointment_id'] = appointment_id
            new_recipe = Recipe(**recipe_data)
            db.add(new_recipe)

    db_appointment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_appointment)

    return db_appointment


import logging


def get_appointments_by_user(
        db: Session,
        user_id: int,
        query: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 1000,
        include_patient: bool = True,
        include_recipes: bool = True,
        include_diagnoses: bool = True
) -> List[Appointment]:
    print("=== INICIO get_appointments_by_user ===")
    print(f"Parámetros recibidos:")
    print(f"  user_id: {user_id} (type: {type(user_id)})")
    print(f"  query: '{query}' (type: {type(query)})")
    print(f"  start_date: {start_date} (type: {type(start_date)})")
    print(f"  end_date: {end_date} (type: {type(end_date)})")
    print(f"  skip: {skip} (type: {type(skip)})")
    print(f"  limit: {limit} (type: {type(limit)})")
    print(f"  include_patient: {include_patient} (type: {type(include_patient)})")
    print(f"  include_recipes: {include_recipes} (type: {type(include_recipes)})")
    print(f"  include_diagnoses: {include_diagnoses} (type: {type(include_diagnoses)})")

    try:
        print("\n--- Paso 1: Creando query base ---")
        db_query = (db.query(Appointment)
                    .filter(Appointment.user_id == user_id)
                    .join(Patient)
                    .outerjoin(AppointmentDiagnosis))
        print("✓ Query base creada exitosamente")

        print("\n--- Paso 2: Aplicando eager loading ---")
        if include_patient:
            print("  Aplicando joinedload para patient...")
            db_query = db_query.options(joinedload(Appointment.patient))
            print("  ✓ joinedload patient aplicado")

        if include_recipes:
            print("  Aplicando joinedload para recipes...")
            db_query = db_query.options(joinedload(Appointment.recipes))
            print("  ✓ joinedload recipes aplicado")

        if include_diagnoses:
            print("  Aplicando joinedload para diagnoses...")
            db_query = db_query.options(joinedload(Appointment.diagnoses))
            print("  ✓ joinedload diagnoses aplicado")

        print("\n--- Paso 3: Preparando condiciones ---")
        conditions = []

        if query and query.strip():
            print(f"  Procesando búsqueda: '{query.strip()}'")
            search_term = f"%{query.lower()}%"
            print(f"  Search term: '{search_term}'")

            print("  ⚠️ ADVERTENCIA: Haciendo JOIN adicional (posible conflicto)")
            db_query = db_query.join(Patient).outerjoin(AppointmentDiagnosis)

            text_conditions = or_(
                func.lower(Patient.first_name).like(search_term),
                func.lower(Patient.last_name).like(search_term),
                Patient.document_id.contains(query.strip()),
                func.lower(AppointmentDiagnosis.diagnosis_description).like(search_term),
                AppointmentDiagnosis.diagnosis_code.contains(query.strip().upper())
            )
            conditions.append(text_conditions)
            print("  ✓ Condiciones de búsqueda agregadas")
        else:
            print("  No hay query de búsqueda")

        if start_date:
            print(f"  Agregando filtro start_date: {start_date}")
            conditions.append(Appointment.appointment_date >= start_date)

        if end_date:
            print(f"  Agregando filtro end_date: {end_date}")
            conditions.append(Appointment.appointment_date <= end_date)

        print(f"  Total condiciones: {len(conditions)}")

        print("\n--- Paso 4: Aplicando filtros ---")
        if conditions:
            print("  Aplicando filtros AND...")
            db_query = db_query.filter(and_(*conditions))
            print("  ✓ Filtros aplicados")
        else:
            print("  No hay condiciones que aplicar")

        print("\n--- Paso 5: Aplicando ordenamiento y paginación ---")
        print(f"  Order by: appointment_date DESC, appointment_time DESC")
        print(f"  Offset: {skip}, Limit: {limit}")

        final_query = (db_query
                       .order_by(desc(Appointment.appointment_date), desc(Appointment.appointment_time))
                       .offset(skip).limit(limit))

        print("  ✓ Ordenamiento y paginación aplicados")

        print("\n--- Paso 6: Ejecutando query ---")
        print("  Ejecutando query...")

        # Mostrar la query SQL generada
        try:
            query_str = str(final_query.statement.compile(compile_kwargs={"literal_binds": True}))
            print(f"  SQL Query: {query_str}")
        except Exception as e:
            print(f"  No se pudo mostrar SQL: {e}")

        result = final_query.all()
        print(f"  ✓ Query ejecutada exitosamente")
        print(f"  Resultados encontrados: {len(result)}")

        if result:
            if hasattr(result[0], 'patient') and result[0].patient:
                print(f"  Primer paciente: {result[0].patient.first_name}")

        print("=== FIN get_appointments_by_user (EXITOSO) ===")
        return result

    except Exception as e:
        if hasattr(e, 'orig'):
            print(f"  Error original: {e.orig}")
        raise




def get_appointment_patient(db: Session, appointment_id: int) -> Optional[AppointmentResponse]:
    """Obtener cita por ID"""
    return (db.query(Appointment)
            .options(
        joinedload(Appointment.patient),
        joinedload(Appointment.recipes),
        joinedload(Appointment.diagnoses)
    )
            .filter(Appointment.id == appointment_id).first())
