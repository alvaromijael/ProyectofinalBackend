from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os
from pyreportjasper import PyReportJasper
from datetime import datetime
import logging
import psycopg2
import base64
import traceback
from fastapi.responses import FileResponse


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])


def verify_database_connection(patient_id: int):
    """Verificar que la conexión y los datos existen"""
    try:
        conn = psycopg2.connect(
            host="13.220.204.70",
            port=5432,
            database="fenixweb",
            user="admin",
            password="admin123"
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

    if not verify_database_connection(patient_id):
        logger.error(f"❌ Paciente {patient_id} no encontrado o no tiene citas")
        raise HTTPException(
            status_code=404,
            detail=f"Paciente {patient_id} no encontrado o no tiene citas registradas"
        )

    input_file = os.path.abspath("reports/MedicalRecord.jrxml")

    if not os.path.exists(input_file):
        logger.error(f"❌ Archivo no encontrado: {input_file}")
        raise HTTPException(status_code=404, detail="Archivo de reporte no encontrado")

    output_dir = os.path.abspath("reports/output")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = int(datetime.now().timestamp())
    output_file = os.path.join(output_dir, f"medical_history_{patient_id}_{timestamp}")

    try:
        pyreportjasper = PyReportJasper()

        db_config = {
            'driver': 'postgres',
            'username': 'admin',
            'password': 'admin123',
            'host': 'localhost',
            'database': 'fenixweb3',
            'port': '5432',
            'jdbc_driver': 'org.postgresql.Driver',
            'jdbc_url': 'jdbc:postgresql://localhost:5432/fenixweb3'
        }

        parameters = {
            'patient_id': patient_id,
            'SUBREPORT_DIR': os.path.abspath("reports") + os.sep
        }
        pyreportjasper.config(
            input_file=input_file,
            output_file=output_file,
            output_formats=["pdf"],
            parameters=parameters,
            db_connection=db_config
        )

        pyreportjasper.process_report()

        pdf_file = f"{output_file}.pdf"

        if not os.path.exists(pdf_file):
            logger.error(f"❌ PDF no generado: {pdf_file}")
            raise HTTPException(status_code=500, detail="PDF no generado")

        with open(pdf_file, "rb") as pdf:
            pdf_bytes = pdf.read()
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

        try:
            os.remove(pdf_file)
        except:
            pass

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


from fastapi.responses import FileResponse


@router.get("/medical-certificate/{appointment_id}")
def get_medical_history_report(appointment_id: int):
    input_file = os.path.abspath("reports/medicalCertificate.jrxml")

    if not os.path.exists(input_file):
        logger.error(f"❌ Archivo no encontrado: {input_file}")
        raise HTTPException(status_code=404, detail="Archivo de reporte no encontrado")

    output_dir = os.path.abspath("reports/output")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = int(datetime.now().timestamp())
    output_file = os.path.join(output_dir, f"medical_certificate_{appointment_id}_{timestamp}")

    try:
        pyreportjasper = PyReportJasper()

        db_config = {
            'driver': 'postgres',
            'username': 'postgres',
            'password': 'sa',
            'host': 'localhost',
            'database': 'fenixweb3',
            'port': '5432',
            'jdbc_driver': 'org.postgresql.Driver',
            'jdbc_url': 'jdbc:postgresql://localhost:5432/fenixweb3'
        }

        parameters = {
            'APPOINTMENT_ID': appointment_id,
        }

        pyreportjasper.config(
            input_file=input_file,
            output_file=output_file,
            output_formats=["pdf"],
            parameters=parameters,
            db_connection=db_config
        )

        pyreportjasper.process_report()

        pdf_file = f"{output_file}.pdf"

        if not os.path.exists(pdf_file):
            logger.error(f"❌ PDF no generado: {pdf_file}")
            raise HTTPException(status_code=500, detail="PDF no generado")

        # Retornar el archivo directamente para descarga
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