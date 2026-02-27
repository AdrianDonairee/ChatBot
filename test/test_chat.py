"""
Tests unitarios para el ChatBot de turnos.

Tests para API REST, AppointmentManager, autenticación y más.
"""
import json
import pytest
from app import create_app
from api import db, TimeSlot
from chatbot_logic import process_message, AppointmentManager
from common import Config


@pytest.fixture
def app():
    """Fixture para crear la aplicación Flask en modo test."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Fixture para el cliente de test de Flask."""
    return app.test_client()


@pytest.fixture
def auth_headers():
    """Headers con token de autenticación."""
    return {
        'X-API-Token': Config.API_TOKEN,
        'Content-Type': 'application/json'
    }


# ========== Tests de API REST ==========

def test_chat_route(client):
    """Test del endpoint de chatbot."""
    res = client.post('/chat/', json={'message': 'Hola bot'})
    assert res.status_code == 200

    data = res.get_json()
    assert 'response' in data
    assert isinstance(data['response'], str)


def test_chat_route_empty_message(client):
    """Test de chatbot con mensaje vacío."""
    res = client.post('/chat/', json={'message': ''})
    assert res.status_code == 400
    
    data = res.get_json()
    assert 'error' in data


def test_turnos_route(client, app):
    """Test del endpoint de listar turnos."""
    with app.app_context():
        # Crear algunos slots de prueba
        slot1 = TimeSlot(datetime_str='2026-03-01 10:00', service='General', customer=None)
        slot2 = TimeSlot(datetime_str='2026-03-01 11:00', service='General', customer='Juan')
        db.session.add_all([slot1, slot2])
        db.session.commit()
    
    res = client.get('/chat/turnos')
    assert res.status_code == 200
    
    data = res.get_json()
    assert 'turnos' in data
    assert isinstance(data['turnos'], list)


def test_turnos_route_with_date_filter(client, app):
    """Test de filtrado de turnos por fecha."""
    with app.app_context():
        slot1 = TimeSlot(datetime_str='2026-03-01 10:00', service='General', customer=None)
        slot2 = TimeSlot(datetime_str='2026-03-02 10:00', service='General', customer=None)
        db.session.add_all([slot1, slot2])
        db.session.commit()
    
    res = client.get('/chat/turnos?date=2026-03-01')
    assert res.status_code == 200
    
    data = res.get_json()
    assert len(data['turnos']) >= 1


def test_turnos_route_invalid_date_format(client):
    """Test de validación de formato de fecha."""
    res = client.get('/chat/turnos?date=01-03-2026')
    assert res.status_code == 400
    
    data = res.get_json()
    assert 'error' in data


def test_reservar_without_auth(client):
    """Test que verifica que reservar requiere autenticación."""
    res = client.post('/chat/reservar', json={
        'slot_id': 1,
        'name': 'Juan',
        'service': 'Corte'
    })
    assert res.status_code == 401  # Unauthorized


def test_reservar_with_valid_auth(client, app, auth_headers):
    """Test de reserva con autenticación válida."""
    with app.app_context():
        slot = TimeSlot(datetime_str='2026-03-01 10:00', service='General', customer=None)
        db.session.add(slot)
        db.session.commit()
        slot_id = slot.id
    
    res = client.post('/chat/reservar', 
                     headers=auth_headers,
                     json={
                         'slot_id': slot_id,
                         'name': 'Juan Pérez',
                         'service': 'Corte'
                     })
    assert res.status_code == 200
    
    data = res.get_json()
    assert data.get('ok') == True


def test_reservar_missing_fields(client, auth_headers):
    """Test de validación de campos requeridos."""
    res = client.post('/chat/reservar',
                     headers=auth_headers,
                     json={'slot_id': 1})  # Falta 'name'
    assert res.status_code == 400


def test_reservar_invalid_service(client, app, auth_headers):
    """Test de validación de servicio."""
    with app.app_context():
        slot = TimeSlot(datetime_str='2026-03-01 10:00', service='General', customer=None)
        db.session.add(slot)
        db.session.commit()
        slot_id = slot.id
    
    res = client.post('/chat/reservar',
                     headers=auth_headers,
                     json={
                         'slot_id': slot_id,
                         'name': 'Juan',
                         'service': 'ServicioInvalido'
                     })
    assert res.status_code == 400


def test_cancelar_without_auth(client):
    """Test que verifica que cancelar requiere autenticación."""
    res = client.post('/chat/cancelar', json={'slot_id': 1})
    assert res.status_code == 401


def test_cancelar_by_slot_id(client, app, auth_headers):
    """Test de cancelación por ID de slot."""
    with app.app_context():
        slot = TimeSlot(datetime_str='2026-03-01 10:00', service='Corte', customer='Juan')
        db.session.add(slot)
        db.session.commit()
        slot_id = slot.id
    
    res = client.post('/chat/cancelar',
                     headers=auth_headers,
                     json={'slot_id': slot_id})
    assert res.status_code == 200


def test_cancelar_by_customer_name(client, app, auth_headers):
    """Test de cancelación por nombre de cliente."""
    with app.app_context():
        slot1 = TimeSlot(datetime_str='2026-03-01 10:00', service='Corte', customer='María')
        slot2 = TimeSlot(datetime_str='2026-03-01 11:00', service='Tinte', customer='María')
        db.session.add_all([slot1, slot2])
        db.session.commit()
    
    res = client.post('/chat/cancelar',
                     headers=auth_headers,
                     json={'name': 'María'})
    assert res.status_code == 200
    
    data = res.get_json()
    assert data.get('cancelados', 0) == 2


# ========== Tests de Procesamiento NLP ==========

def test_process_message_greeting():
    """Test de procesamiento de saludo."""
    response = process_message("hola")
    assert "Hola" in response or "hola" in response


def test_process_message_unknown():
    """Test de respuesta a mensaje desconocido."""
    response = process_message("xyzabc123")
    assert "entend" in response.lower() or "otra forma" in response.lower()


# ========== Tests de AppointmentManager ==========

def test_appointment_manager_initialization():
    """Test de inicialización del gestor de turnos."""
    am = AppointmentManager(db_uri='sqlite:///:memory:')
    assert am is not None


def test_list_available_slots():
    """Test de listar slots disponibles."""
    am = AppointmentManager(db_uri='sqlite:///:memory:')
    slots = am.list_available()
    assert isinstance(slots, list)


def test_book_slot():
    """Test de reservar un slot."""
    am = AppointmentManager(db_uri='sqlite:///:memory:')
    slots = am.list_available()
    
    if slots:
        slot_id = slots[0]['id']
        result = am.book(slot_id, 'Test User', 'Corte')
        assert result == True
        
        # Verificar que no está disponible
        updated_slot = am.find_slot(slot_id)
        assert updated_slot['customer'] == 'Test User'


def test_book_nonexistent_slot():
    """Test de reservar un slot inexistente."""
    am = AppointmentManager(db_uri='sqlite:///:memory:')
    result = am.book(99999, 'Test User', 'Corte')
    assert result == False


def test_cancel_by_slot():
    """Test de cancelar reserva por ID."""
    am = AppointmentManager(db_uri='sqlite:///:memory:')
    slots = am.list_available()
    
    if slots:
        slot_id = slots[0]['id']
        am.book(slot_id, 'Test User', 'Corte')
        
        result = am.cancel_by_slot(slot_id)
        assert result == True
        
        # Verificar que está disponible nuevamente
        updated_slot = am.find_slot(slot_id)
        assert updated_slot['customer'] is None


def test_cancel_by_customer():
    """Test de cancelar todas las reservas de un cliente."""
    am = AppointmentManager(db_uri='sqlite:///:memory:')
    slots = am.list_available()
    
    if len(slots) >= 2:
        # Reservar dos slots para el mismo cliente
        am.book(slots[0]['id'], 'Test User', 'Corte')
        am.book(slots[1]['id'], 'Test User', 'Tinte')
        
        # Cancelar todas
        count = am.cancel_by_customer('Test User')
        assert count == 2


def test_list_bookings():
    """Test de listar reservas activas."""
    am = AppointmentManager(db_uri='sqlite:///:memory:')
    slots = am.list_available()
    
    if slots:
        am.book(slots[0]['id'], 'Test User', 'Corte')
        
        bookings = am.list_bookings()
        assert len(bookings) >= 1
        assert bookings[0]['customer'] == 'Test User'


# ========== Tests de Configuración ==========

def test_config_values():
    """Test de que Config tiene los valores esperados."""
    assert hasattr(Config, 'FLASK_HOST')
    assert hasattr(Config, 'FLASK_PORT')
    assert hasattr(Config, 'DATABASE_URI')
    assert hasattr(Config, 'API_TOKEN')


# ========== Tests de Autenticación ==========

def test_invalid_token(client):
    """Test con token inválido."""
    res = client.post('/chat/reservar',
                     headers={'X-API-Token': 'invalid-token'},
                     json={'slot_id': 1, 'name': 'Test', 'service': 'Corte'})
    assert res.status_code == 403


def test_missing_token(client):
    """Test sin token."""
    res = client.post('/chat/reservar',
                     json={'slot_id': 1, 'name': 'Test', 'service': 'Corte'})
    assert res.status_code == 401
