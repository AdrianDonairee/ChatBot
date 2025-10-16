import json
from app import create_app

def test_chat_route():
    app = create_app()
    client = app.test_client()

    res = client.post('/chat/', json={'message': 'Hola bot'})
    assert res.status_code == 200

    data = res.get_json()
    assert 'response' in data
    assert isinstance(data['response'], str)
