# UnicoNet - Red Social Universitaria

Red social desarrollada con Django, PostgreSQL y Docker para la comunidad universitaria.

## Tecnologias

- Python 3.11+
- Django 5.0+
- PostgreSQL 15
- Docker & Docker Compose
- Django REST Framework

## Modulos Principales

- **authentication**: Sistema de autenticacion y autorizacion
- **users**: Gestion de usuarios
- **profiles**: Perfiles personalizados de usuarios
- **posts**: Sistema de publicaciones
- **comments**: Comentarios en publicaciones
- **likes**: Sistema de me gusta
- **friends**: Sistema de amistades
- **groups**: Grupos universitarios
- **notifications**: Sistema de notificaciones
- **messages**: Mensajeria privada
- **feed**: Feed personalizado de noticias
- **events**: Eventos universitarios

## Instalacion

### Con Docker (Recomendado)

```bash
# Construir contenedores
docker-compose build

# Iniciar servicios
docker-compose up -d

# Crear migraciones
docker-compose exec web python manage.py makemigrations

# Aplicar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser
```

### Sin Docker

```bash
# Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
```

## Estructura del Proyecto

```
uniconet/
â”œâ”€â”€ apps/              # Aplicaciones Django
â”œâ”€â”€ uniconet/          # Configuracion principal
â”œâ”€â”€ static/            # Archivos estaticos
â”œâ”€â”€ media/             # Archivos subidos
â”œâ”€â”€ templates/         # Templates globales
â”œâ”€â”€ utils/             # Utilidades
â””â”€â”€ tests/             # Tests
```

## Variables de Entorno

Crear archivo `.env`:

```
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/uniconet_db
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Caracteristicas

- Autenticacion y autorizacion completa
- Perfiles personalizables
- Publicaciones con multimedia
- Sistema de comentarios
- Sistema de likes
- Amistades y seguidores
- Grupos universitarios
- Notificaciones en tiempo real
- Mensajeria privada
- Feed personalizado
- Eventos y calendario

## Testing

```bash
# Ejecutar todos los tests
python manage.py test

# Tests de una app especifica
python manage.py test apps.authentication
```

## Licencia

Este proyecto esta bajo la Licencia MIT.

## Contacto

Universidad Politecnica Estatal del Carchi - UPEC
