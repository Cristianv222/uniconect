#!/bin/bash

# Script de entrada para el contenedor Django
set -e

echo "======================================"
echo "  Iniciando UnicoNet - Entrypoint"
echo "======================================"

# Esperar a que PostgreSQL este listo
echo "Esperando a PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.5
done
echo "PostgreSQL esta listo!"

# Esperar a que Redis este listo
echo "Esperando a Redis..."
while ! nc -z redis 6379; do
  sleep 0.5
done
echo "Redis esta listo!"

# Crear directorios si no existen
mkdir -p /app/static /app/media

# Aplicar migraciones
echo "Aplicando migraciones..."
python manage.py makemigrations --noinput || true
python manage.py migrate --noinput || true

# Recolectar archivos estaticos (solo si no es runserver)
if [ "$1" != "python" ] || [ "$2" != "manage.py" ] || [ "$3" != "runserver" ]; then
    echo "Recolectando archivos estaticos..."
    python manage.py collectstatic --noinput --clear || true
fi

echo "======================================"
echo "  UnicoNet esta listo!"
echo "======================================"

# Ejecutar el comando pasado al contenedor
exec "$@"