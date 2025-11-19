# Script para crear la estructura completa de UnicoNet
# Ejecutar desde PowerShell dentro de tu repositorio
# .\create_structure.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GENERADOR DE ESTRUCTURA UNICONET      " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar ubicacion
$currentLocation = Get-Location
Write-Host "Ubicacion actual: $currentLocation" -ForegroundColor Yellow
Write-Host ""
Write-Host "IMPORTANTE: Este script creara archivos y carpetas aqui." -ForegroundColor Yellow
Write-Host ""
Write-Host "Continuar? (S/N): " -NoNewline -ForegroundColor White
$confirm = Read-Host

if ($confirm -ne "S" -and $confirm -ne "s") {
    Write-Host ""
    Write-Host "Operacion cancelada por el usuario." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Iniciando creacion de estructura..." -ForegroundColor Green
Write-Host ""

# Contador de elementos creados
$filesCreated = 0
$dirsCreated = 0

# Funcion para crear archivos
function New-ProjectFile {
    param([string]$Path)
    try {
        $null = New-Item -ItemType File -Path $Path -Force -ErrorAction Stop
        $script:filesCreated++
        Write-Host "  [OK] $Path" -ForegroundColor Gray
        return $true
    }
    catch {
        Write-Host "  [ERROR] $Path - $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Funcion para crear directorios
function New-ProjectDirectory {
    param([string]$Path)
    try {
        $null = New-Item -ItemType Directory -Path $Path -Force -ErrorAction Stop
        $script:dirsCreated++
        return $true
    }
    catch {
        Write-Host "  [ERROR] $Path - $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# 1. ARCHIVOS RAIZ
Write-Host "[1/8] Creando archivos raiz..." -ForegroundColor Cyan

$rootFiles = @(
    ".gitignore",
    "docker-compose.yml", 
    "dockerfile",
    "entrypoint.sh",
    "manage.py",
    "requirements.txt",
    "README.md"
)

foreach ($file in $rootFiles) {
    $null = New-ProjectFile -Path $file
}

Write-Host ""

# 2. CONFIGURACION PRINCIPAL (uniconet/)
Write-Host "[2/8] Creando configuracion principal (uniconet/)..." -ForegroundColor Cyan

$null = New-ProjectDirectory -Path "uniconet"

$configFiles = @(
    "uniconet/__init__.py",
    "uniconet/settings.py",
    "uniconet/urls.py",
    "uniconet/wsgi.py",
    "uniconet/asgi.py"
)

foreach ($file in $configFiles) {
    $null = New-ProjectFile -Path $file
}

Write-Host ""

# 3. CARPETA APPS
Write-Host "[3/8] Creando carpeta apps/..." -ForegroundColor Cyan

$null = New-ProjectDirectory -Path "apps"
$null = New-ProjectFile -Path "apps/__init__.py"
$null = New-ProjectFile -Path "apps/context_processors.py"

Write-Host ""

# 4. CREAR TODAS LAS APLICACIONES
Write-Host "[4/8] Creando aplicaciones..." -ForegroundColor Cyan

$apps = @(
    @{
        name = "authentication"
        extras = @("decorators.py")
        hasManagement = $true
        commands = @("create_initial_data.py")
    },
    @{
        name = "users"
        extras = @()
        hasManagement = $false
        commands = @()
    },
    @{
        name = "profiles"
        extras = @()
        hasManagement = $false
        commands = @()
    },
    @{
        name = "posts"
        extras = @("signals.py")
        hasManagement = $true
        commands = @("cleanup_posts.py")
    },
    @{
        name = "comments"
        extras = @()
        hasManagement = $false
        commands = @()
    },
    @{
        name = "likes"
        extras = @()
        hasManagement = $false
        commands = @()
    },
    @{
        name = "friends"
        extras = @()
        hasManagement = $false
        commands = @()
    },
    @{
        name = "groups"
        extras = @()
        hasManagement = $false
        commands = @()
    },
    @{
        name = "notifications"
        extras = @("signals.py")
        hasManagement = $false
        commands = @()
    },
    @{
        name = "messages"
        extras = @("signals.py")
        hasManagement = $false
        commands = @()
    },
    @{
        name = "feed"
        extras = @()
        hasManagement = $false
        commands = @()
    },
    @{
        name = "events"
        extras = @()
        hasManagement = $false
        commands = @()
    }
)

foreach ($app in $apps) {
    $appName = $app.name
    Write-Host "  -> Creando app: $appName" -ForegroundColor Yellow
    
    # Directorio principal de la app
    $appPath = "apps/$appName"
    $null = New-ProjectDirectory -Path $appPath
    
    # Archivos estandar de Django
    $standardFiles = @(
        "__init__.py",
        "admin.py",
        "apps.py",
        "models.py",
        "views.py",
        "urls.py",
        "forms.py",
        "serializers.py",
        "tests.py",
        "permissions.py"
    )
    
    foreach ($file in $standardFiles) {
        $null = New-ProjectFile -Path "$appPath/$file"
    }
    
    # Archivos extras
    foreach ($extra in $app.extras) {
        $null = New-ProjectFile -Path "$appPath/$extra"
    }
    
    # Migrations
    $null = New-ProjectDirectory -Path "$appPath/migrations"
    $null = New-ProjectFile -Path "$appPath/migrations/__init__.py"
    
    # Templates
    $null = New-ProjectDirectory -Path "$appPath/templates/$appName"
    
    # Static
    $null = New-ProjectDirectory -Path "$appPath/static/$appName"
    
    # Management commands
    if ($app.hasManagement) {
        $null = New-ProjectDirectory -Path "$appPath/management/commands"
        $null = New-ProjectFile -Path "$appPath/management/__init__.py"
        $null = New-ProjectFile -Path "$appPath/management/commands/__init__.py"
        
        foreach ($cmd in $app.commands) {
            $null = New-ProjectFile -Path "$appPath/management/commands/$cmd"
        }
    }
}

Write-Host ""

# 5. CARPETAS STATIC Y MEDIA
Write-Host "[5/8] Creando carpetas static/ y media/..." -ForegroundColor Cyan

# Static
$null = New-ProjectDirectory -Path "static/css"
$null = New-ProjectDirectory -Path "static/js"
$null = New-ProjectDirectory -Path "static/img"
$null = New-ProjectDirectory -Path "static/icons"
Write-Host "  [OK] static/ (css, js, img, icons)" -ForegroundColor Gray

# Media
$null = New-ProjectDirectory -Path "media/profiles"
$null = New-ProjectDirectory -Path "media/posts"
$null = New-ProjectDirectory -Path "media/groups"
$null = New-ProjectDirectory -Path "media/events"
Write-Host "  [OK] media/ (profiles, posts, groups, events)" -ForegroundColor Gray

Write-Host ""

# 6. TEMPLATES GLOBALES
Write-Host "[6/8] Creando templates globales..." -ForegroundColor Cyan

$null = New-ProjectDirectory -Path "templates/base"
$null = New-ProjectDirectory -Path "templates/components"

$templateFiles = @(
    "templates/base.html",
    "templates/base_authenticated.html",
    "templates/components/navbar.html",
    "templates/components/sidebar.html",
    "templates/components/post_card.html",
    "templates/components/user_card.html"
)

foreach ($file in $templateFiles) {
    $null = New-ProjectFile -Path $file
}

Write-Host ""

# 7. UTILS
Write-Host "[7/8] Creando carpeta utils/..." -ForegroundColor Cyan

$null = New-ProjectDirectory -Path "utils"

$utilsFiles = @(
    "utils/__init__.py",
    "utils/helpers.py",
    "utils/validators.py",
    "utils/decorators.py",
    "utils/mixins.py"
)

foreach ($file in $utilsFiles) {
    $null = New-ProjectFile -Path $file
}

Write-Host ""

# 8. TESTS
Write-Host "[8/8] Creando carpeta tests/..." -ForegroundColor Cyan

$null = New-ProjectDirectory -Path "tests"

$testFiles = @(
    "tests/__init__.py",
    "tests/test_authentication.py",
    "tests/test_posts.py",
    "tests/test_friends.py"
)

foreach ($file in $testFiles) {
    $null = New-ProjectFile -Path $file
}

Write-Host ""

# GENERAR CONTENIDO DE .GITIGNORE
Write-Host "Generando contenido de .gitignore..." -ForegroundColor Cyan

@'
# Python
*.py[cod]
*$py.class
*.so
__pycache__/
*.egg-info/
dist/
build/

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
/media
/staticfiles

# Environment
.env
.venv
env/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Docker
*.pid
'@ | Set-Content -Path ".gitignore"

Write-Host "  [OK] .gitignore generado" -ForegroundColor Gray
Write-Host ""

# GENERAR CONTENIDO DE README.MD
Write-Host "Generando contenido de README.md..." -ForegroundColor Cyan

@'
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
├── apps/              # Aplicaciones Django
├── uniconet/          # Configuracion principal
├── static/            # Archivos estaticos
├── media/             # Archivos subidos
├── templates/         # Templates globales
├── utils/             # Utilidades
└── tests/             # Tests
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
'@ | Set-Content -Path "README.md" -Encoding UTF8

Write-Host "  [OK] README.md generado" -ForegroundColor Gray
Write-Host ""

# RESUMEN FINAL
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   ESTRUCTURA CREADA CON EXITO         " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Estadisticas:" -ForegroundColor Cyan
Write-Host "  - Directorios creados: $dirsCreated" -ForegroundColor White
Write-Host "  - Archivos creados: $filesCreated" -ForegroundColor White
Write-Host "  - Aplicaciones: 12" -ForegroundColor White
Write-Host ""
Write-Host "Aplicaciones creadas:" -ForegroundColor Yellow
foreach ($app in $apps) {
    Write-Host "  * $($app.name)" -ForegroundColor White
}
Write-Host ""
Write-Host "Proximos pasos:" -ForegroundColor Yellow
Write-Host "  1. Configurar entorno virtual" -ForegroundColor White
Write-Host "     python -m venv venv" -ForegroundColor Gray
Write-Host "     venv\Scripts\activate" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Instalar dependencias" -ForegroundColor White
Write-Host "     pip install django djangorestframework psycopg2" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Configurar settings.py" -ForegroundColor White
Write-Host "     - SECRET_KEY" -ForegroundColor Gray
Write-Host "     - DATABASES" -ForegroundColor Gray
Write-Host "     - INSTALLED_APPS" -ForegroundColor Gray
Write-Host ""
Write-Host "Presiona Enter para salir..." -ForegroundColor Cyan
$null = Read-Host