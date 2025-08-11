import sys
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import json
import csv
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configura o PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# Variáveis globais para as funções
inicializar_chatbot = None
get_chatbot_answer_stream = None
criar_e_salvar_indice_estruturado = None

# Importa as funções do chatbot
try:
    from chatbot.chatbot import inicializar_chatbot as _inicializar_chatbot, get_chatbot_answer_stream as _get_chatbot_answer_stream
    inicializar_chatbot = _inicializar_chatbot
    get_chatbot_answer_stream = _get_chatbot_answer_stream
    
    try:
        from criar_indice_estruturado import criar_e_salvar_indice_estruturado as _criar_e_salvar_indice_estruturado
        criar_e_salvar_indice_estruturado = _criar_e_salvar_indice_estruturado
    except ImportError:
        def criar_e_salvar_indice_estruturado():
            pass

except ImportError as e:
    def inicializar_chatbot():
        return True
    
    def get_chatbot_answer_stream(pergunta):
        yield "data: " + json.dumps({"answer": "Serviço em manutenção. Por favor, tente novamente mais tarde."}) + "\n\n"
        
    def criar_e_salvar_indice_estruturado():
        pass

# Inicializa o Flask
app = Flask(__name__)

# Configura CORS
CORS_ORIGIN = os.getenv('CORS_ORIGIN', 'https://projeto-bia.vercel.app')
CORS(app, resources={r"/*": {
    "origins": [CORS_ORIGIN],
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type"]
}})

# Configuração do arquivo de feedback
FEEDBACK_FILE = os.path.join(os.path.dirname(__file__), 'feedback.csv')

# Função para verificar e processar dados
def verificar_e_processar_dados():
    indice_path = os.path.join(os.path.dirname(__file__), '..', 'faiss_index_estruturado')
    if not os.path.exists(indice_path):
        criar_e_salvar_indice_estruturado()

# Tenta inicializar o chatbot
try:
    verificar_e_processar_dados()
    chatbot_pronto = inicializar_chatbot()
except Exception as e:
    chatbot_pronto = True

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "Backend do Chatbot está funcionando!",
        "version": "1.0.0"
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/chat', methods=['GET'])
def chat():
    pergunta = request.args.get('message')

    if not pergunta:
        def error_stream():
            error_data = {"error": "Nenhuma mensagem foi fornecida."}
            yield "data: " + json.dumps(error_data) + "\n\n"
        return Response(error_stream(), mimetype='text/event-stream')

    return Response(get_chatbot_answer_stream(pergunta), mimetype='text/event-stream')

@app.route('/api/auth', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')

    if username == admin_username and password == admin_password:
        return jsonify({
            "status": "success",
            "message": "Login realizado com sucesso!",
            "user": {"username": username, "role": "admin"}
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Credenciais inválidas."
        }), 401

@app.route('/feedback', methods=['POST'])
def salvar_feedback():
    try:
        data = request.get_json()
        question = data.get('question')
        answer = data.get('answer')
        feedback_type = data.get('feedback')

        if not all([question, answer, feedback_type]):
            return jsonify({"status": "error", "message": "Dados incompletos."}, 400)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, question, answer, feedback_type]

        file_exists = os.path.isfile(FEEDBACK_FILE)
        with open(FEEDBACK_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Question", "Answer", "Feedback"])
            writer.writerow(row)

        return jsonify({"status": "success", "message": "Feedback recebido com sucesso!"})
    except Exception as e:
        return jsonify({"status": "error", "message": "Erro interno ao salvar feedback."}, 500)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
