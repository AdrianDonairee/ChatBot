"""
Rutas del API REST para el ChatBot de turnos.

Endpoints:
    POST /chat/           - Chatbot de procesamiento de lenguaje
    GET  /chat/turnos     - Listar turnos disponibles
    POST /chat/reservar   - Reservar un turno
    POST /chat/cancelar   - Cancelar una reserva
    GET  /chat/ui         - Interfaz web HTML
"""
from flask import Blueprint, request, jsonify, render_template_string
import logging
from chatbot_logic import process_message, AppointmentManager
from api import db, Appointment

# Configurar logger
logger = logging.getLogger(__name__)

# Blueprint principal
chat_blueprint = Blueprint('chat', __name__)

# Servicios permitidos (validación)
ALLOWED_SERVICES = ['Corte', 'Barba', 'Tinte', 'Peinado', 'General']

@chat_blueprint.route('/', methods=['POST'])
def chat():
    """
    Procesa mensajes del chatbot usando procesamiento de lenguaje simple.
    
    Request Body (JSON):
        message (str): Mensaje del usuario
    
    Returns:
        JSON: {'response': str} con la respuesta del bot
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        user_message = data.get('message', '')
       
    Devuelve lista de turnos disponibles.
    
    Query Parameters:
        date (str, opcional): Fecha en formato YYYY-MM-DD para filtrar
    
    Returns:
        JSON: {'turnos': [lista de turnos con disponibilidad]}
    """
    try:
        date = request.args.get('date')
        
        # Validar formato de fecha si se proporciona
        if date:
            import re
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
                return jsonify({
                    'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }), 400
        
        am = AppointmentManager()
        slots = am.list_available(date) if date else am.list_available()

        # Marcar los turnos que ya fueron reservados en la BD
        booked = {a.slot_id: a for a in Appointment.query.all()}
        annotated = []
        
        for s in slots:
            slot_id = int(s.get('id'))
            if slot_id in booked:
                # Este turno está en BD (reservado)
                a = booked[slot_id]
                s['customer'] = a.customer
                s['service'] = a.service or s.get('service')
            else:
                # Turno libre
                s['customer'] = s.get('customer')
            annotated.append(s)
        
        logger.info(f"Listados {len(annotated)} turnos" + (f" para fecha {date}" if date else ""))
        return jsonify({'turnos': annotated})
        
    except Exception as e:
       
    Reserva un turno específico para un cliente.
    
    Request Body (JSON):
        slot_id (int): ID del turno a reservar
        name (str): Nombre del cliente
        service (str, opcional): Tipo de servicio (default: 'General')
    
    Returns:
        JSON: {'ok': bool, 'error': str (si falla)}
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        slot_id = data.get('slot_id')
        name = data.get('name')
        service = data.get('service', 'General')
        
        # Validaciones
        if not slot_id or not name:
            return jsonify({
                'error': 'Los campos slot_id y name son obligatorios'
            }), 400

        try:
            slot_id = int(slot_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'slot_id debe ser un número entero'}), 400
        
        if not isinstance(name, str) or len(name.strip()) == 0:
            return jsonify({'error': 'name debe ser un string no vacío'}), 400
        
        if len(name) > 128:
            return jsonify({'error': 'name no puede exceder 128 caracteres'}), 400
       
    Cancela una o más reservas.
    
    Request Body (JSON):
        Opción 1: {"slot_id": int} - Cancela por ID
        Opción 2: {"name": str} - Cancela todos los turnos del cliente
    
    Returns:
        JSON: {'ok': bool, 'cancelados': int, 'deleted_db_rows': int}
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        am = AppointmentManager()
        
        if 'slot_id' in data:
            # Cancelar por ID
            try:
                slot_id = int(data['slot_id'])
            except (ValueError, TypeError):
                return jsonify({'error': 'slot_id debe ser un número entero'}), 400
            
            ok = am.cancel_by_slot(slot_id)
            deleted = Appointment.query.filter_by(slot_id=slot_id).delete()
            db.session.commit()
            
            logger.info(f"Cancelación por ID: slot={slot_id}, exitosa={ok}, filas_bd={deleted}")
            return jsonify({'ok': ok, 'deleted_db_rows': deleted})
        
        elif 'name' in data:
            # Cancelar por nombre
            name = data['name']
            if not isinstance(name, str) or len(name.strip()) == 0:
                return jsonify({'error': 'name debe ser un string no vacío'}), 400
            
            n = am.cancel_by_customer(name.strip())
            deleted = Appointment.query.filter_by(customer=name.strip()).delete()
            db.session.commit()
            
            logger.info(f"Cancelación por nombre: cliente={name}, cancelados={n}, filas_bd={deleted}")
            return jsonify({'cancelados': n, 'deleted_db_rows': deleted})
        
        else:
            return jsonify({
                'error': 'Debe proveer slot_id o name para cancelar'
            }), 400
    
    except Exception as e:
        logger.error(f"Error en endpoint /cancelar: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 5t_id).first()
        if existing:
            # Actualizar existente
            existing.customer = name.strip()
            existing.service = service
        else:
            # Crear nuevo
            existing = Appointment(
                slot_id=slot_id,
                customer=name.strip(),
                service=service
            )
            db.session.add(existing)
        
        db.session.commit()
        logger.info(f"✓ Reserva exitosa: slot={slot_id}, cliente={name}, servicio={service}")
        return jsonify({'ok': True})
        
    except Exception as e:
        logger.error(f"Error en endpoint /reservar: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500)
    name = data.get('name')
    service = data.get('service', 'General')
    if not slot_id or not name:
        return jsonify({'error': 'slot_id y name son requeridos'}), 400

    try:
        slot_id = int(slot_id)
    except Exception:
        return jsonify({'error': 'slot_id inválido'}), 400

    am = AppointmentManager()
    ok = am.book(slot_id, name, service)

    if not ok:
        return jsonify({'ok': False, 'error': 'slot no disponible'}), 200

    # persistir en la DB (si ya existe, actualizar)
    existing = Appointment.query.filter_by(slot_id=slot_id).first()
    if existing:
        existing.customer = name
        existing.service = service
    else:
        existing = Appointment(slot_id=slot_id, customer=name, service=service)
        db.session.add(existing)
    db.session.commit()
    return jsonify({'ok': True})


@chat_blueprint.route('/cancelar', methods=['POST'])
def cancelar():
    """Cancelar por id o por nombre. JSON: {"slot_id": int} o {"name": str}"""
    data = request.get_json(force=True, silent=True) or {}
    am = AppointmentManager()
    if 'slot_id' in data:
        try:
            slot_id = int(data['slot_id'])
        except Exception:
            return jsonify({'error': 'slot_id inválido'}), 400
        ok = am.cancel_by_slot(slot_id)
        # eliminar de la BD si existía
        deleted = Appointment.query.filter_by(slot_id=slot_id).delete()
        db.session.commit()
        return jsonify({'ok': ok, 'deleted_db_rows': deleted})
    if 'name' in data:
        n = am.cancel_by_customer(data['name'])
        # eliminar de la BD por customer
        deleted = Appointment.query.filter_by(customer=data['name']).delete()
        db.session.commit()
        return jsonify({'cancelados': n, 'deleted_db_rows': deleted})
    return jsonify({'error': 'proveer slot_id o name'}), 400


@chat_blueprint.route('/ui', methods=['GET'])
def ui():
    """Página web sencilla para listar y reservar turnos desde el navegador."""
    html = '''
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Turnos - Peluquería</title>
        <style>body{font-family:Arial,Helvetica,sans-serif;margin:20px} table{border-collapse:collapse} td,th{border:1px solid #ddd;padding:6px}</style>
    </head>
    <body>
        <h2>Turnos disponibles</h2>
        <div>
            Fecha (YYYY-MM-DD): <input id="date" />
            <button onclick="load()">Filtrar</button>
            <button onclick="load(true)">Mostrar todos</button>
        </div>
        <div id="list"></div>
        <h3>Reservar</h3>
        <div>
            ID: <input id="slot_id" size="4" /> Nombre: <input id="name" /> Servicio: <input id="service" />
            <button onclick="reserve()">Reservar</button>
        </div>
        <script>
            async function load(all=false){
                let date = document.getElementById('date').value;
                let url = '/chat/turnos';
                if(!all && date) url += '?date='+encodeURIComponent(date);
                const res = await fetch(url);
                const data = await res.json();
                const turnos = data.turnos || [];
                let html = '<table><tr><th>ID</th><th>Fecha</th><th>Servicio</th><th>Estado</th></tr>';
                for(let t of turnos){
                    html += `<tr><td>${t.id}</td><td>${t.datetime}</td><td>${t.service}</td><td>${t.customer?('Reservado por '+t.customer):'Libre'}</td></tr>`;
                }
                html += '</table>';
                document.getElementById('list').innerHTML = html;
            }
            async function reserve(){
                const slot_id = document.getElementById('slot_id').value;
                const name = document.getElementById('name').value;
                const service = document.getElementById('service').value;
                const res = await fetch('/chat/reservar', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({slot_id:parseInt(slot_id), name, service})});
                const data = await res.json();
                alert('Resultado: '+JSON.stringify(data));
                load();
            }
            // cargar al inicio
            load();
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)
