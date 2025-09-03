FROM tiangolo/uvicorn-gunicorn-fastapi:latest

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
# ENV PORT=8000
ENV APP_MODULE=main:app
# CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "main:app"]

# FROM python:3.11-slim

# Establecer directorio de trabajo
# WORKDIR /app

# Copiar requirements.txt primero (para mejor cache de Docker)
# COPY requirements.txt .

# Instalar dependencias Python
 # RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la aplicación
# COPY . .

# Exponer el puerto 8000
# EXPOSE 8000

# NO incluimos CMD - Railway usará el Launch command