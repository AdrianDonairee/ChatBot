from .responses import RESPONSES
import re

def _clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-záéíóúüñ\s]', '', text)
    return text.strip()

def process_message(message: str) -> str:
    msg = _clean_text(message)
    # búsqueda simple por palabras clave
    for key, value in RESPONSES.items():
        if key in msg:
            return value
    # respuesta por defecto
    return "No entendí eso 🤔, ¿podés decirlo de otra forma?"
