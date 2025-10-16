FROM python:3.11-bullseye

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64 \
    PATH="${JAVA_HOME}/bin:${PATH}"

# Instalar dependencias del sistema
RUN echo "deb http://deb.debian.org/debian bullseye contrib non-free" >> /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian-security bullseye-security contrib non-free" >> /etc/apt/sources.list && \
    apt-get update && \
    echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | debconf-set-selections && \
    apt-get install -y --no-install-recommends \
        openjdk-11-jdk \
        fontconfig \
        fonts-dejavu \
        fonts-liberation \
        ttf-mscorefonts-installer \
        cabextract \
        curl && \
    fc-cache -f -v && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Verificar instalaciones
RUN java -version && \
    fc-list | grep -i arial || echo "Warning: Arial font not found"

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias Python (separado para mejor cache)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/reports/output

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]