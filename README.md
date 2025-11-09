# ChatBot
Chatbot sencillo con API Flask y un cliente CLI para gestionar turnos de peluquería.

Características principales:
- API Flask básica en `app.py` (ruta `/chat/` en `api/routes.py`).
- Lógica del bot en `chatbot_logic/processor.py` y respuestas en `chatbot_logic/responses.py`.
- Gestor de turnos persistente simple en `chatbot_logic/appointments.py` (almacena en `instance/appointments.json`).
- Interfaz por terminal: `run_chatbot.py` permite listar, reservar y cancelar turnos.

Cómo ejecutar el chatbot por terminal
1. Asegurate de tener las dependencias (ver `requirements.txt`). Por ejemplo:

```powershell
python -m pip install -r requirements.txt
```

2. Ejecutar el CLI interactivo:

```powershell
python run_chatbot.py
```

3. Opciones en la terminal:
- Mostrar turnos disponibles (posible filtrar por fecha YYYY-MM-DD)
- Reservar por id (pedirá nombre y servicio)
- Cancelar por id o por nombre del cliente
- Listar reservas activas
- Chatear con el procesador simple (palabras clave)

Notas
- Los turnos iniciales se generan automáticamente (próximos 7 días, horarios fijos). Los datos se guardan en `instance/appointments.json`.
- La API Flask existente sigue funcionando y el test `test/test_chat.py` usa esa API mínima.

Si querés, puedo:
- Añadir validaciones de formato de fecha más estrictas.
- Añadir confirmaciones por email (simulado) o integración con calendario.
- Mejorar el NLP del `processor.py` para entender frases como "quiero un turno el viernes".

