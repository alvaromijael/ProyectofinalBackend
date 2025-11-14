from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import os
from pyreportjasper import PyReportJasper
from datetime import datetime
import logging
import psycopg2
import base64
import traceback
from urllib.parse import urlparse

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])


# Parsear DATABASE_URL para extraer credenciales
def parse_database_url():
    """Extraer información de conexión desde DATABASE_URL"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL no está configurado en las variables de entorno")

    # Remover el prefijo postgresql+psycopg2:// o postgresql://
    url = database_url
    if url.startswith("postgresql+psycopg2://"):
        url = url.replace("postgresql+psycopg2://", "postgresql://")
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://")

    parsed = urlparse(url)

    return {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'database': parsed.path.lstrip('/'),
        'user': parsed.username,
        'password': parsed.password
    }


# Obtener configuración de la base de datos
db_info = parse_database_url()
DB_HOST = db_info['host']
DB_PORT = db_info['port']
DB_NAME = db_info['database']
DB_USER = db_info['user']
DB_PASSWORD = db_info['password']

logger.info(f"📊 Configuración DB - Host: {DB_HOST}, Port: {DB_PORT}, Database: {DB_NAME}, User: {DB_USER}")

# Rutas de archivos (opcionales como variables de entorno)
REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "reports/output")


def get_db_config():
    """Obtener configuración de base de datos para JasperReports"""
    return {
        'driver': 'postgres',
        'username': DB_USER,
        'password': DB_PASSWORD,
        'host': DB_HOST,
        'database': DB_NAME,
        'port': str(DB_PORT),
        'jdbc_driver': 'org.postgresql.Driver',
        'jdbc_url': f'jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}'
    }


def verify_database_connection(patient_id: int):
    """Verificar que la conexión y los datos existen"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.id, COUNT(a.id) as appointment_count
            FROM medical.patients p
            LEFT JOIN medical.appointments a ON a.patient_id = p.id
            WHERE p.id = %s
            GROUP BY p.id
        """, (patient_id,))

        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            patient_id_found, appointment_count = result
            if appointment_count == 0:
                return False
            return True
        else:
            return False

    except Exception as e:
        logger.error(f"❌ Error verificando BD: {e}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        return False


@router.get("/medical-history/{patient_id}")
def get_medical_history_report(patient_id: int):
    """Genera reporte de historial médico del paciente"""

    if not verify_database_connection(patient_id):
        logger.error(f"❌ Paciente {patient_id} no encontrado o no tiene citas")
        raise HTTPException(
            status_code=404,
            detail=f"Paciente {patient_id} no encontrado o no tiene citas registradas"
        )

    input_file = os.path.abspath(os.path.join(REPORTS_DIR, "MedicalRecord.jrxml"))

    if not os.path.exists(input_file):
        logger.error(f"❌ Archivo no encontrado: {input_file}")
        raise HTTPException(status_code=404, detail="Archivo de reporte no encontrado")

    output_dir = os.path.abspath(OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)

    timestamp = int(datetime.now().timestamp())
    output_file = os.path.join(output_dir, f"medical_history_{patient_id}_{timestamp}")

    try:
        pyreportjasper = PyReportJasper()

        parameters = {
            'patient_id': patient_id,
            'SUBREPORT_DIR': os.path.abspath(REPORTS_DIR) + os.sep
        }

        pyreportjasper.config(
            input_file=input_file,
            output_file=output_file,
            output_formats=["pdf"],
            parameters=parameters,
            db_connection=get_db_config()
        )

        pyreportjasper.process_report()

        pdf_file = f"{output_file}.pdf"

        if not os.path.exists(pdf_file):
            logger.error(f"❌ PDF no generado: {pdf_file}")
            raise HTTPException(status_code=500, detail="PDF no generado")

        with open(pdf_file, "rb") as pdf:
            pdf_bytes = pdf.read()
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

        # Limpiar archivo temporal
        try:
            os.remove(pdf_file)
        except Exception as cleanup_error:
            logger.warning(f"No se pudo eliminar archivo temporal: {cleanup_error}")

        return JSONResponse(
            content={
                "success": True,
                "patient_id": patient_id,
                "filename": f"historial_medico_paciente_{patient_id}.pdf",
                "pdf_base64": pdf_base64,
                "size_bytes": len(pdf_bytes),
                "generated_at": datetime.now().isoformat()
            },
            status_code=200
        )

    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/medical-certificate/{appointment_id}")
def get_medical_certificate_report(appointment_id: int):
    """Genera certificado médico para una cita"""

    input_file = os.path.abspath(os.path.join(REPORTS_DIR, "medicalCertificate.jrxml"))

    if not os.path.exists(input_file):
        logger.error(f"❌ Archivo no encontrado: {input_file}")
        raise HTTPException(status_code=404, detail="Archivo de reporte no encontrado")

    output_dir = os.path.abspath(OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)

    timestamp = int(datetime.now().timestamp())
    output_file = os.path.join(output_dir, f"medical_certificate_{appointment_id}_{timestamp}")

    try:
        pyreportjasper = PyReportJasper()

        parameters = {
            'APPOINTMENT_ID': appointment_id,
        }

        pyreportjasper.config(
            input_file=input_file,
            output_file=output_file,
            output_formats=["pdf"],
            parameters=parameters,
            db_connection=get_db_config()
        )

        pyreportjasper.process_report()

        pdf_file = f"{output_file}.pdf"

        if not os.path.exists(pdf_file):
            logger.error(f"❌ PDF no generado: {pdf_file}")
            raise HTTPException(status_code=500, detail="PDF no generado")

        filename = f"certificado_medico_{appointment_id}.pdf"

        return FileResponse(
            path=pdf_file,
            media_type='application/pdf',
            filename=filename,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))