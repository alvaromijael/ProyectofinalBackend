import os
import subprocess
from datetime import datetime

# Configuración
JASPER_STARTER = r"C:\Users\Boris\Desktop\Jasper\jasperstarter.exe"


def generate_recipe_report(appointment_id: int,
                           db_host: str = "localhost",
                           db_port: str = "5432",
                           db_name: str = "femixweb3",
                           db_user: str = "postgres",
                           db_password: str = "sa") -> str:
    os.makedirs("tmp", exist_ok=True)
    report_path = "reports/Recipe.jrxml"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"tmp/Recipe_{timestamp}"

    try:
        # Crear archivo batch temporal para ejecutar con permisos
        batch_content = f'''@echo off
cd /d "{os.getcwd()}"
"{JASPER_STARTER}" process "{report_path}" -f pdf -o "{output_file}" -t postgres -H {db_host} -u {db_user} -p {db_password} -n {db_name} --db-port {db_port} -P filtro={appointment_id}
'''

        batch_file = "tmp/run_jasper.bat"
        with open(batch_file, 'w') as f:
            f.write(batch_content)

        # Ejecutar el batch con permisos elevados
        result = subprocess.run([
            "powershell",
            "Start-Process",
            f'"{batch_file}"',
            "-Verb", "RunAs",
            "-Wait"
        ], capture_output=True, text=True, check=True)

        pdf_file = f"{output_file}.pdf"
        if os.path.exists(pdf_file):
            return pdf_file
        else:
            raise Exception("No se generó el archivo PDF")

    except subprocess.CalledProcessError as e:
        raise Exception(f"Error generando reporte: {e.stderr}")