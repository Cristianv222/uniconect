"""
Configuracion de Celery para UnicoNet
Para tareas asincronas como:
- Envio de emails
- Procesamiento de imagenes
- Generacion de reportes
- Limpieza de datos antiguos
"""

import os
from celery import Celery

# Configurar el modulo de settings de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uniconet.settings')

# Crear instancia de Celery
app = Celery('uniconet')

# Cargar configuracion desde Django settings
# namespace='CELERY' significa que todas las configuraciones
# de Celery deben tener el prefijo CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodescubrir tareas en todas las apps registradas
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Tarea de debug para probar Celery"""
    print(f'Request: {self.request!r}')


# Configuraciones de Celery (agregar al settings.py si usas Celery):
"""
# En settings.py:

# Celery Configuration
CELERY_BROKER_URL = f"redis://{config('REDIS_HOST', default='localhost')}:{config('REDIS_PORT', default='6379')}/0"
CELERY_RESULT_BACKEND = f"redis://{config('REDIS_HOST', default='localhost')}:{config('REDIS_PORT', default='6379')}/0"
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutos
"""

# Para iniciar Celery worker:
# celery -A uniconet worker -l info

# Para iniciar Celery beat (tareas programadas):
# celery -A uniconet beat -l info