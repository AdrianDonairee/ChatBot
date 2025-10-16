from flask import Blueprint, request, jsonify
from chatbot_logic.processor import process_message

chat_blueprint = Blueprint('chat', __name__)

@chat_blueprint.route('/', methods=['POST'])
def chat():
    data = request.get_json(force=True, silent=True) or {}
    user_message = data.get('message', '')
    if not isinstance(user_message, str):
        return jsonify({'error': 'mensaje no válido'}), 400

    response = process_message(user_message)
    return jsonify({'response': response})
