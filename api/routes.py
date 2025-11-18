from flask import Blueprint, request, jsonify, render_template_string
from chatbot_logic.processor import process_message
from services.reservation_service import ReservationService

chat_blueprint = Blueprint('chat', __name__)


@chat_blueprint.route('/', methods=['POST'])
def chat():
        data = request.get_json(force=True, silent=True) or {}
        user_message = data.get('message', '')
        if not isinstance(user_message, str):
                return jsonify({'error': 'mensaje no válido'}), 400

        response = process_message(user_message)
        return jsonify({'response': response})


@chat_blueprint.route('/turnos', methods=['GET'])
def get_turnos():
        """Devuelve lista de turnos disponibles. Query param opcional: date=YYYY-MM-DD"""
        date = request.args.get('date')
        svc = ReservationService()
        slots = svc.list_available(date) if date else svc.list_available()
        return jsonify({'turnos': slots})


@chat_blueprint.route('/reservar', methods=['POST'])
def reservar():
        """Reservar un turno por id. JSON: {"slot_id": int, "name": str, "service": str}"""
        data = request.get_json(force=True, silent=True) or {}
        slot_id = data.get('slot_id')
        name = data.get('name')
        service = data.get('service', 'General')
        if not slot_id or not name:
                return jsonify({'error': 'slot_id y name son requeridos'}), 400
        svc = ReservationService()
        ok = svc.book(int(slot_id), name, service)
        return jsonify({'ok': ok})


@chat_blueprint.route('/cancelar', methods=['POST'])
def cancelar():
        """Cancelar por id o por nombre. JSON: {"slot_id": int} o {"name": str}"""
        data = request.get_json(force=True, silent=True) or {}
        svc = ReservationService()
        if 'slot_id' in data:
                ok = svc.cancel_by_slot(int(data['slot_id']))
                return jsonify({'ok': ok})
        if 'name' in data:
                n = svc.cancel_by_customer(data['name'])
                return jsonify({'cancelados': n})
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
