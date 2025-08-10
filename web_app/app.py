from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import sys
import json
import csv
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configura o PYTHONPATH e imprime para debug
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
print(f"🔍 PYTHONPATH atual: {sys.path}")
print(f"📂 Diretório atual: {os.getcwd()}")
print(f"📂 Conteúdo do diretório:")
for item in os.listdir(os.getcwd()):
    print(f"  - {item}")


# Importa as funções do chatbot com fallback e mais logs
try:
    print("🔄 Tentando importar módulo chatbot...")
    chatbot_path = os.path.join(os.getcwd(), 'chatbot')
    print(f"📂 Verificando diretório chatbot: {chatbot_path}")
    if os.path.exists(chatbot_path):
        print(f"✅ Diretório chatbot encontrado em: {chatbot_path}")
    else:
        print(f"⚠️ Diretório chatbot não encontrado em: {chatbot_path}")
    
    from chatbot.chatbot import inicializar_chatbot, get_chatbot_answer_stream
    print("✅ Módulo chatbot importado com sucesso")
    
    # Adicionado: Importa a função de criação de índice
    from criar_indice_estruturado import criar_e_salvar_indice_estruturado

except ImportError as e:
    print(f"⚠️ Erro ao importar chatbot: {e}")
    print("⚠️ Criando funções mock para inicialização...")
    
    def inicializar_chatbot():
        print("⚠️ Função mock: inicializar_chatbot")
        return True  # Alterado para True para permitir testes
    
    def get_chatbot_answer_stream(pergunta):
        print(f"⚠️ Função mock: get_chatbot_answer_stream - {pergunta}")
        yield "data: " + json.dumps({"answer": "Serviço em manutenção. Por favor, tente novamente mais tarde."}) + "\n\n"
        
    # Adicionado: Mock para a função de criação de índice
    def criar_e_salvar_indice_estruturado():
        print("⚠️ Função mock: criar_e_salvar_indice_estruturado")
        pass

# Inicializa o Flask
app = Flask(__name__)

# Configura CORS
CORS_ORIGIN = os.getenv('CORS_ORIGIN', '*')
CORS(app, resources={r"/*": {"origins": CORS_ORIGIN}})

chatbot_pronto = False
FEEDBACK_FILE = os.path.join(os.path.dirname(__file__), 'feedback.csv')

def verificar_e_processar_dados():
    """Verifica se os dados foram processados, se não, executa os scripts"""
    try:
        base_conhecimento_path = os.path.join(os.path.dirname(__file__), 'base_conhecimento_precisao.csv')
        faiss_index_path = os.path.join(os.path.dirname(__file__), 'faiss_index_estruturado')
        
        if not os.path.exists(base_conhecimento_path) or not os.path.exists(faiss_index_path):
            print("🔧 Primeira execução ou índice não encontrado: Processando dados...")
            # Chama a função para criar o índice
            criar_e_salvar_indice_estruturado()
            
        return True
    except Exception as e:
        print(f"⚠️ Erro ao verificar e processar dados: {e}")
        return False # Retorna False para indicar que a inicialização falhou


# Inicialização para produção
print("--- Iniciando Servidor Flask e Chatbot ---")
verificar_e_processar_dados()

try:
    chatbot_pronto = inicializar_chatbot()
    if chatbot_pronto:
        print("--- Chatbot inicializado com sucesso ---")
    else:
        print("!!! Aviso: Falha ao inicializar o chatbot !!!")
except Exception as e:
    import traceback
    print(f"!!! ERRO CRÍTICO AO INICIALIZAR CHATBOT: {e} !!!")
    traceback.print_exc() # This will print the full stack trace
    print("!!! Servidor vai iniciar sem chatbot - apenas para debug !!!")
    chatbot_pronto = True  # Alterado para True para permitir testes

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "Backend do Chatbot está funcionando!",
        "version": "1.0.0"
    })

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
def authenticate():
    """Endpoint para autenticação de usuários"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Buscar credenciais das variáveis de ambiente
        valid_username = os.environ.get('ADMIN_USERNAME', 'admin')
        valid_password = os.environ.get('ADMIN_PASSWORD', 'boticario2024')
        
        if username == valid_username and password == valid_password:
            return jsonify({"status": "success", "message": "Autenticação bem-sucedida"})
        else:
            return jsonify({"status": "error", "message": "Credenciais inválidas"}), 401
    except Exception as e:
        print(f"Erro na autenticação: {e}")
        return jsonify({"status": "error", "message": "Erro interno de autenticação"}), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        data = request.get_json()
        question = data.get('question')
        answer = data.get('answer')
        feedback_type = data.get('feedback')

        if not all([question, answer, feedback_type]):
            return jsonify({"status": "error", "message": "Dados de feedback incompletos."}), 400

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
        print(f"Erro ao salvar feedback: {e}")
        return jsonify({"status": "error", "message": "Erro interno ao salvar feedback."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)