# ChatBot - Sistema de Gestión de Turnos 💈

Sistema completo de gestión de turnos para peluquería con múltiples interfaces de acceso.

## 📋 Características

- ✅ **API REST Flask** - Endpoints HTTP para integración web
- ✅ **Servidor TCP Socket** - Protocolo alternativo multihilo
- ✅ **CLI Interactivo** - Interfaz de terminal para gestión directa
- ✅ **Chatbot NLP** - Procesamiento básico de lenguaje natural
- ✅ **Persistencia Dual** - JSON + Base de datos SQLAlchemy
- ✅ **Worker Asincrónico** - Procesamiento de tareas via IPC
- ✅ **Logging Robusto** - Sistema de logs estructurado
- ✅ **Docker Ready** - Configuración completa para containers

## 🏗️ Estructura del Proyecto

```
backend/
├── api/                    # API REST Flask
│   ├── __init__.py        # Exports públicos
│   ├── db.py              # SQLAlchemy instance
│   ├── models.py          # Modelos de BD
│   └── routes.py          # Endpoints HTTP
├── chatbot_logic/         # Lógica del chatbot
│   ├── __init__.py
│   ├── processor.py       # Procesamiento NLP
│   ├── appointments.py    # Gestor de turnos
│   └── responses.py       # Base de conocimiento
├── services/              # Capa de servicios
│   ├── __init__.py
│   └── reservation_service.py
├── socket_srv/            # Servidor TCP
│   ├── __init__.py
│   └── server.py
├── worker/                # Worker asincrónico
│   ├── __init__.py
│   └── worker.py
├── app.py                 # Aplicación Flask principal
├── run_chatbot.py         # CLI interactivo
└── requirements.txt       # Dependencias
```

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
copy .env.example .env

# Editar .env con tus configuraciones
# En Linux/Mac: cp .env.example .env
```

## ⚙️ Configuración

El archivo `.env` permite configurar:

```env
# Flask
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True

# Base de datos
DATABASE_URL=sqlite:///instance/appointments.db

# Socket Server
SOCKET_HOST=0.0.0.0
SOCKET_PORT=5001

# Logging
LOG_LEVEL=INFO

# Secret Key (CAMBIAR EN PRODUCCIÓN)
SECRET_KEY=your-secret-key-here
```

## 🎯 Modos de Ejecución

### Opción 1: API REST (Flask)

```bash
python app.py
```

Accede en: `http://localhost:5000`

**Endpoints disponibles:**
- `POST /chat/` - Chatbot
- `GET /chat/turnos` - Listar turnos
- `POST /chat/reservar` - Reservar turno
- `POST /chat/cancelar` - Cancelar reserva
- `GET /chat/ui` - Interfaz web HTML

### Opción 2: Servidor TCP Socket

```bash
python -m socket_srv.server --host 0.0.0.0 --port 5001
```

**Comandos disponibles:**
```
LIST [YYYY-MM-DD]      - Lista turnos disponibles
BOOK id|name|service   - Reserva un turno
CANCEL_ID <id>         - Cancela por ID
CANCEL_NAME <nombre>   - Cancela por nombre
QUIT                   - Cierra conexión
```

**Conectar con telnet:**
```bash
telnet localhost 5001
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
docker-compose up
```

Inicia Flask + PostgreSQL en containers.

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con coverage
pytest --cov=. --cov-report=html

# Test específico
pytest test/test_chat.py
```

## 📡 Ejemplos de Uso

### Reservar turno via API REST

```bash
curl -X POST http://localhost:5000/chat/reservar \
  -H "Content-Type: application/json" \
  -d '{"slot_id": 5, "name": "Juan", "service": "Corte"}'
```

### Listar turnos via API REST

```bash
curl http://localhost:5000/chat/turnos?date=2026-02-25
```

### Chatear con el bot

```bash
curl -X POST http://localhost:5000/chat/ \
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

## 📄 Licencia

[Tu licencia aquí]

## 👥 Autores

[Tus datos aquí]

## 🐛 Reportar Issues

[Link a issues de GitHub]

---

**¿Necesitas ayuda?** Revisa la documentación en `/docs` o abre un issue.
