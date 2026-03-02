# ChatBot - Sistema de Gestión de Turnos 💈

Sistema completo de gestión de turnos para peluquería con múltiples interfaces de acceso y arquitectura moderna.

## 📋 Características

- ✅ **API REST Flask** - Endpoints HTTP con autenticación por token
- ✅ **Servidor TCP Socket** - Protocolo multihilo con comando HELP
- ✅ **CLI Interactivo** - Interfaz de terminal para gestión directa
- ✅ **Chatbot NLP** - Procesamiento básico de lenguaje natural
- ✅ **Persistencia Unificada** - SQLAlchemy compartida entre todas las interfaces
- ✅ **Worker Asincrónico** - Procesamiento de tareas via IPC
- ✅ **Logging Centralizado** - Sistema de logs estructurado configurable
- ✅ **Configuración Centralizada** - Módulo `common/` para configuración compartida
- ✅ **Autenticación** - Protección de endpoints críticos con tokens
- ✅ **Docker Ready** - Docker Compose con múltiples servicios

## 🏗️ Estructura del Proyecto

```
backend/
├── api/                    # API REST Flask
│   ├── __init__.py        # Exports públicos
│   ├── auth.py            # ✨ Sistema de autenticación
│   ├── db.py              # SQLAlchemy instance
│   ├── models.py          # Modelos de BD (TimeSlot)
│   └── routes.py          # Endpoints HTTP protegidos
├── chatbot_logic/         # Lógica del chatbot
│   ├── __init__.py
│   ├── processor.py       # Procesamiento NLP
│   ├── appointments.py    # ✨ Gestor con SQLAlchemy
│   └── responses.py       # Base de conocimiento
├── common/                # ✨ Configuración centralizada
│   ├── __init__.py
│   ├── config.py          # Config unificada
│   └── logconfig.py       # Logging centralizado
├── services/              # Capa de servicios
│   ├── __init__.py
│   └── reservation_service.py
├── socket_srv/            # Servidor TCP
│   ├── __init__.py
│   └── server.py          # ✨ Con comando HELP
├── worker/                # Worker asincrónico
│   ├── __init__.py
│   └── worker.py
├── test/                  # Tests unitarios
│   └── test_chat.py
├── app.py                 # Aplicación Flask principal
├── run_chatbot.py         # CLI interactivo
├── docker-compose.yml     # ✨ Orquestación completa
├── .env.example           # ✨ Configuración de ejemplo
└── requirements.txt       # Dependencias
```

## ✨ Novedades y Mejoras

### 1. **Persistencia Unificada**
Todas las interfaces (API, Socket, CLI) ahora comparten la **misma base de datos SQLAlchemy**. 
- ❌ Antes: JSON para CLI/Socket + SQLite para API (desincronizados)
- ✅ Ahora: Una sola fuente de verdad en base de datos

### 2. **Autenticación de API**
Endpoints de escritura protegidos con tokens:
```bash
curl -X POST http://localhost:5000/chat/reservar \
  -H "X-API-Token: dev-token-123" \
  -H "Content-Type: application/json" \
  -d '{"slot_id": 1, "name": "Juan", "service": "Corte"}'
```

### 3. **Configuración Centralizada**
Módulo `common/` con `Config` y `setup_logging()` usados por todos los componentes.

### 4. **Comando HELP en Socket**
El servidor socket ahora incluye ayuda interactiva:
```
> HELP
╔════════════════════════════════════════════════════╗
║    SERVIDOR DE TURNOS - COMANDOS DISPONIBLES      ║
╚════════════════════════════════════════════════════╝
...
```

### 5. **Docker Compose Mejorado**
Orquestación completa con healthchecks y networking:
- PostgreSQL con persistencia
- API REST
- Socket Server
- Worker (opcional)

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone <tu-repo>
cd ChatBot/backend
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
# Dependencias de producción
pip install -r requirements.txt

# Dependencias de desarrollo (opcional)
pip install -r requirements-dev.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
copy .env.example .env    # Windows
cp .env.example .env      # Linux/Mac

# Editar .env con tus configuraciones
```

## ⚙️ Configuración

El archivo `.env` permite configurar:

```env
# Flask API
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-cambiar-en-produccion

# Base de datos (UNIFICADA)
DATABASE_URL=sqlite:///instance/appointments.db
# Para PostgreSQL: postgresql://user:pass@host:5432/db

# Socket Server
SOCKET_HOST=0.0.0.0
SOCKET_PORT=5001

# Worker
WORKER_SLEEP_TIME=0.1

# Autenticación
API_TOKEN=dev-token-123

# Logging
LOG_LEVEL=INFO
```

## 🎯 Modos de Ejecución

### Opción 1: API REST (Flask)

```bash
python app.py
```

Accede en: `http://localhost:5000`

**Endpoints disponibles:**

#### Públicos (sin autenticación):
- `POST /chat/` - Chatbot NLP
  ```bash
  curl -X POST http://localhost:5000/chat/ \
    -H "Content-Type: application/json" \
    -d '{"message": "hola"}'
  ```

- `GET /chat/turnos` - Listar turnos disponibles
  ```bash
  curl http://localhost:5000/chat/turnos
  curl http://localhost:5000/chat/turnos?date=2026-03-01
  ```

#### Protegidos (requieren X-API-Token):
- `POST /chat/reservar` - Reservar turno
  ```bash
  curl -X POST http://localhost:5000/chat/reservar \
    -H "X-API-Token: dev-token-123" \
    -H "Content-Type: application/json" \
    -d '{"slot_id": 1, "name": "Juan Pérez", "service": "Corte"}'
  ```

- `POST /chat/cancelar` - Cancelar reserva
  ```bash
  # Por ID
  curl -X POST http://localhost:5000/chat/cancelar \
    -H "X-API-Token: dev-token-123" \
    -H "Content-Type: application/json" \
    -d '{"slot_id": 5}'
  
  # Por nombre
  curl -X POST http://localhost:5000/chat/cancelar \
    -H "X-API-Token: dev-token-123" \
    -H "Content-Type: application/json" \
    -d '{"name": "Juan Pérez"}'
  ```

### Opción 2: Servidor TCP Socket

```bash
python -m socket_srv.server --host 0.0.0.0 --port 5001
```

**Comandos disponibles:**
```
HELP o ?               - Muestra ayuda con todos los comandos
LIST [YYYY-MM-DD]      - Lista turnos disponibles
BOOK id|name|service   - Reserva un turno
CANCEL_ID <id>         - Cancela por ID de slot
CANCEL_NAME <nombre>   - Cancela todas las reservas del cliente
QUIT o EXIT            - Cierra conexión
```

**Conectar con telnet:**
```bash
telnet localhost 5001

> HELP
> LIST
> BOOK 1|Juan Pérez|Corte
> QUIT
```

### Opción 3: CLI Interactivo

```bash
python run_chatbot.py
```

Menú con opciones para:
1. Mostrar turnos disponibles
2. Reservar un turno
3. Cancelar un turno
4. Listar reservas activas
5. Chatear con el bot
6. Salir

### Opción 4: Docker Compose

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Reiniciar un servicio específico
docker-compose restart api
```

**Servicios incluidos:**
- `db` - PostgreSQL 15 con persistencia
- `api` - Flask REST API en puerto 5000
- `socket_server` - Servidor TCP en puerto 5001

**Configurar variables de entorno para Docker:**
```bash
# Crear .env con configuración de producción
export SECRET_KEY=your-production-secret-key
export API_TOKEN=your-production-token
docker-compose up -d
```

## 🏛️ Arquitectura

### Flujo de Datos Unificado

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  API REST   │────▶│              │◀────│ Socket TCP  │
│  (Flask)    │     │  SQLAlchemy  │     │ (Multihilo) │
└─────────────┘     │              │     └─────────────┘
                    │   Database   │
┌─────────────┐     │              │     ┌─────────────┐
│     CLI     │────▶│  (Unified)   │◀────│   Worker    │
│ Interactive │     │              │     │  (Async)    │
└─────────────┘     └──────────────┘     └─────────────┘
```

**Ventaja:** Todas las interfaces comparten la misma base de datos.
Una reserva hecha por la API es visible en el Socket Server y viceversa.

### Componentes Principales

1. **`common/`** - Configuración y utilidades compartidas
   - `Config` - Parámetros centralizados
   - `setup_logging()` - Logging uniforme

2. **`api/`** - API REST
   - Autenticación con tokens
   - Endpoints protegidos (reservar, cancelar)
   - Endpoints públicos (listar, chatbot)

3. **`socket_srv/`** - Servidor TCP
   - Threading para múltiples clientes
   - Protocolo de texto plano
   - Comando HELP interactivo

4. **`worker/`** - Procesamiento asíncrono
   - IPC con multiprocessing.Queue
   - Tareas de escritura sin bloquear

5. **`chatbot_logic/`** - Lógica de negocio
   - `AppointmentManager` con SQLAlchemy
   - NLP básico con regex
   - Generación automática de slots

## 🧪 Testing

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=. --cov-report=html

# Test específico
pytest test/test_chat.py -v

# Ver reporte de coverage
open htmlcov/index.html  # Linux/Mac
start htmlcov/index.html  # Windows
```

## 📡 Ejemplos de Uso Completos

### 1. Reservar turno via API REST (con autenticación)

```bash
curl -X POST http://localhost:5000/chat/reservar \
  -H "X-API-Token: dev-token-123" \
  -H "Content-Type: application/json" \
  -d '{"slot_id": 5, "name": "Juan Pérez", "service": "Corte"}'

# Respuesta exitosa:
# {"ok": true}
```

### 2. Listar turnos disponibles

```bash
# Todos los turnos
curl http://localhost:5000/chat/turnos

# Filtrar por fecha
curl "http://localhost:5000/chat/turnos?date=2026-03-01"
```

### 3. Chatear con el bot

```bash
curl -X POST http://localhost:5000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "hola, quiero información sobre horarios"}'

# Respuesta:
# {"response": "¡Hola! 😊 ¿En qué puedo ayudarte?"}
```

### 4. Usar el servidor socket

```bash
# Conectar con telnet
telnet localhost 5001

# O con netcat
nc localhost 5001

# Comandos:
> HELP
> LIST
> BOOK 3|María González|Tinte
> CANCEL_ID 3
> QUIT
```

### 5. Cancelar reservas

```bash
# Por ID de slot
curl -X POST http://localhost:5000/chat/cancelar \
  -H "X-API-Token: dev-token-123" \
  -H "Content-Type: application/json" \
  -d '{"slot_id": 5}'

# Por nombre de cliente
curl -X POST http://localhost:5000/chat/cancelar \
  -H "X-API-Token: dev-token-123" \
  -H "Content-Type: application/json" \
  -d '{"name": "Juan Pérez"}'
```

## 🔒 Seguridad

### Autenticación de API

Los endpoints de escritura requieren un token en el header:

```bash
# Header requerido
X-API-Token: tu-token-aqui
```

**Generar un token seguro:**
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Y configurarlo en `.env`:
```env
API_TOKEN=el_token_generado_aqui
```

### Buenas prácticas

1. ✅ Cambiar `SECRET_KEY` y `API_TOKEN` en producción
2. ✅ Usar PostgreSQL en producción (no SQLite)
3. ✅ Configurar `FLASK_DEBUG=False` en producción
4. ✅ Usar HTTPS con certificados SSL/TLS
5. ✅ No commitear el archivo `.env` al repositorio

## 🐛 Troubleshooting

### Error: "No module named 'common'"

```bash
# Asegurarse de estar en el directorio backend
cd backend

# Verificar que common/ existe
ls common/
```

### Error: "Database locked" (SQLite)

SQLite tiene limitaciones de concurrencia. Usar PostgreSQL:

```env
# En .env
DATABASE_URL=postgresql://user:pass@localhost:5432/chatbot
```

### Puerto ya en uso

```bash
# Ver qué proceso usa el puerto
# Windows:
netstat -ano | findstr :5000

# Linux/Mac:
lsof -i :5000

# Cambiar puerto en .env
FLASK_PORT=5001
```

## 📚 Documentación Adicional

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Python Socket Programming](https://docs.python.org/3/library/socket.html)
- [Multiprocessing Guide](https://docs.python.org/3/library/multiprocessing.html)

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama (`git checkout -b feature/mejora`)
3. Commit cambios (`git commit -am 'Agregar mejora'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto es de código abierto bajo la licencia MIT.

## 👥 Autores

- Desarrollado como proyecto académico para Computación 2

## 🎓 Conceptos Demostrados

Este proyecto demuestra:
- ✅ **Concurrencia** - Threading y Multiprocessing
- ✅ **IPC** - Inter-Process Communication con colas
- ✅ **Protocolos de red** - HTTP/REST y TCP puro
- ✅ **Persistencia** - ORM con SQLAlchemy
- ✅ **Arquitecturas** - Cliente-servidor, microservicios
- ✅ **Buenas prácticas** - Logging, configuración, testing
- ✅ **Contenedores** - Docker y orquestación
- ✅ **Seguridad** - Autenticación y autorización
  -H "Content-Type: application/json" \
  -d '{"message": "Hola, ¿cómo estás?"}'
```

### Reservar via Socket TCP

```bash
telnet localhost 5001
> BOOK 5|Juan|Corte
```

## 📊 Servicios Permitidos

- Corte
- Barba
- Tinte
- Peinado
- General

## 🔒 Seguridad

**⚠️ IMPORTANTE para producción:**

1. Cambiar `SECRET_KEY` en `.env` a un valor seguro:
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

2. Establecer `FLASK_DEBUG=False`

3. Usar base de datos PostgreSQL en lugar de SQLite

4. Configurar HTTPS/TLS para el servidor TCP

## 🛠️ Desarrollo

### Formatear código

```bash
black .
isort .
```

### Linting

```bash
flake8 .
pylint backend/
```

### Type checking

```bash
mypy backend/
```

## 📝 Logs

Los logs se configuran via `LOG_LEVEL` en `.env`:

- `DEBUG` - Información detallada
- `INFO` - Eventos normales (recomendado)
- `WARNING` - Advertencias
- `ERROR` - Errores
- `CRITICAL` - Errores críticos

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 👥 Autores

Adrian donaire
Gaston bravo

**¿Necesitas ayuda?** Revisa la documentación en `/docs` o abre un issue.
