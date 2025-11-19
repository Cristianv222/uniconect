# Dockerfile para desarrollo de UnicoNet
FROM python:3.11-slim

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar el proyecto
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/static /app/media

# Dar permisos de ejecución al entrypoint
RUN chmod +x /app/entrypoint.sh

# Exponer puerto
EXPOSE 8000

# Punto de entrada
ENTRYPOINT ["/app/entrypoint.sh"]

# Comando por defecto
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]