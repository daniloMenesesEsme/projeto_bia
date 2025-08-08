from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import sys
import json
import csv
import subprocess
from datetime import datetime, timedelta
from dotenv import load_dotenv
import jwt
from functools import wraps

load_dotenv()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa as funções do chatbot com fallback
try:
    from chatbot.chatbot import inicializar_chatbot, get_chatbot_answer_stream
    print("✅ Módulo chatbot importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar chatbot: {e}")
    print("🔧 Criando funções mock para inicialização...")
    
    def inicializar_chatbot():
        print("⚠️ Função mock: inicializar_chatbot")
        return False
    
    def get_chatbot_answer_stream(pergunta):
        print(f"⚠️ Função mock: get_chatbot_answer_stream - {pergunta}")
        yield "data: " + json.dumps({"error": "Chatbot não disponível"}) + "\n\n"

app = Flask(__name__)

# Configuração de CORS para produção e desenvolvimento
cors_origins = [
    "https://javisgb.vercel.app", # Frontend em produção
    "http://localhost:3000",      # Frontend em desenvolvimento local
    "http://127.0.0.1:3000"       # Outra variação de localhost
]

CORS(app, origins=cors_origins, supports_credentials=True)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'uma-chave-secreta-muito-forte')

# Headers de segurança
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
    return response

chatbot_pronto = False
FEEDBACK_FILE = os.path.join(os.path.dirname(__file__), 'feedback.csv')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token é obrigatório!'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['username']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirou!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token é inválido!'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

def verificar_e_processar_dados():
    """Verifica se os dados foram processados, se não, executa os scripts"""
    base_conhecimento_path = os.path.join(os.path.dirname(__file__), 'base_conhecimento_precisao.csv')
    faiss_index_path = os.path.join(os.path.dirname(__file__), 'faiss_index_estruturado')
    
    if not os.path.exists(base_conhecimento_path) or not os.path.exists(faiss_index_path):
        print("🔄 Primeira execução: Processando dados...")
        
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
        # Processar PDFs
        try:
            print("📄 Processando PDFs...")
            subprocess.run([sys.executable, 'scripts/processar_documentos_pypdf.py'], 
                         cwd=root_dir, check=True, capture_output=True, text=True)
            print("✅ PDFs processados!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao processar PDFs: {e}")
            print(f"Saída: {e.stdout}")
            print(f"Erro: {e.stderr}")
        except Exception as e:
            print(f"❌ Erro inesperado ao processar PDFs: {e}")
        
        # Limpar dados
        try:
            print("🧹 Limpando dados...")
            subprocess.run([sys.executable, 'scripts/limpar_dados.py'], 
                         cwd=root_dir, check=True, capture_output=True, text=True)
            print("✅ Dados limpos!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao limpar dados: {e}")
            print(f"Saída: {e.stdout}")
            print(f"Erro: {e.stderr}")
        except Exception as e:
            print(f"❌ Erro inesperado ao limpar dados: {e}")
        
        # Criar índice FAISS
        try:
            print("🔍 Criando índice FAISS...")
            subprocess.run([sys.executable, 'web_app/criar_indice_estruturado.py'], 
                         cwd=root_dir, check=True, capture_output=True, text=True)
            print("✅ Índice FAISS criado!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao criar índice FAISS: {e}")
            print(f"Saída: {e.stdout}")
            print(f"Erro: {e.stderr}")
        except Exception as e:
            print(f"❌ Erro inesperado ao criar índice FAISS: {e}")
        
        print("✅ Processamento de dados concluído!")
    else:
        print("✅ Dados já processados, pulando processamento inicial...")

# Inicialização automática para deploy
print("🚀 --- Iniciando Servidor Flask e Chatbot ---")
verificar_e_processar_dados()

try:
    chatbot_pronto = inicializar_chatbot()
    if chatbot_pronto:
        print("✅ --- Chatbot inicializado com sucesso ---")
    else:
        print("⚠️ !!! Aviso: Falha ao inicializar o chatbot !!!")
except Exception as e:
    print(f"❌ !!! Erro ao inicializar chatbot: {e} !!!")
    print("⚠️ !!! Servidor vai iniciar sem chatbot - apenas para debug !!!")
    chatbot_pronto = False

@app.route('/')
def home():
    return "✅ Backend do Chatbot está funcionando!"

@app.route('/health')
def health_check():
    """Endpoint para verificação de saúde da aplicação"""
    return jsonify({
        "status": "healthy",
        "chatbot_ready": chatbot_pronto,
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    })

@app.route('/chat', methods=['GET'])
@token_required
def chat(current_user):
    if not chatbot_pronto:
        def error_stream():
            error_data = {"error": "O Chatbot ainda não está pronto."}
            yield "data: " + json.dumps(error_data) + "\n\n"
        return Response(error_stream(), mimetype='text/event-stream')

    pergunta = request.args.get('message')

    if not pergunta:
        def error_stream():
            error_data = {"error": "Nenhuma mensagem foi fornecida."}
            yield "data: " + json.dumps(error_data) + "\n\n"
        return Response(error_stream(), mimetype='text/event-stream')

    return Response(get_chatbot_answer_stream(pergunta), mimetype='text/event-stream')

@app.route('/api/auth', methods=['POST'])
def authenticate():
    """Endpoint para autenticação de usuários"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        valid_username = os.environ.get('ADMIN_USERNAME', 'admin')
        valid_password = os.environ.get('ADMIN_PASSWORD', 'boticario2024')
        
        if username == valid_username and password == valid_password:
            token = jwt.encode({
                'username': username,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            return jsonify({"status": "success", "token": token})
        else:
            return jsonify({"status": "error", "message": "Credenciais inválidas"}), 401
    except Exception as e:
        print(f"❌ Erro na autenticação: {e}")
        return jsonify({"status": "error", "message": "Erro interno de autenticação"}), 500

@app.route('/feedback', methods=['POST'])
@token_required
def feedback(current_user):
    try:
        data = request.get_json()
        question = data.get('question')
        answer = data.get('answer')
        feedback_type = data.get('feedback')

        if not all([question, answer, feedback_type]):
            return jsonify({"status": "error", "message": "Dados de feedback incompletos."}), 400

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, question, answer, feedback_type, current_user]

        file_exists = os.path.isfile(FEEDBACK_FILE)
        with open(FEEDBACK_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Question", "Answer", "Feedback", "User"])
            writer.writerow(row)

        return jsonify({"status": "success", "message": "Feedback recebido com sucesso!"})
    except Exception as e:
        print(f"❌ Erro ao salvar feedback: {e}")
        return jsonify({"status": "error", "message": "Erro interno ao salvar feedback."}), 500

if __name__ == '__main__':
    print("🚀 --- Iniciando Servidor Flask em Produção ---")
    
    port = int(os.environ.get('PORT', 5001))
    
    if chatbot_pronto:
        print(f"✅ --- Servidor rodando na porta {port} ---")
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        print("⚠️ !!! Falha ao inicializar o chatbot. O servidor não será iniciado. !!!")
        app.run(host='0.0.0.0', port=port, debug=False)
