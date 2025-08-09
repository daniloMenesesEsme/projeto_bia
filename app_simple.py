#!/usr/bin/env python3
"""
Versão simplificada da aplicação para teste no Railway
"""
import os
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import jwt
from functools import wraps

app = Flask(__name__)

# Configuração básica
CORS(app, origins=["https://javisgb.vercel.app", "http://localhost:3000"])
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'uma-chave-secreta-muito-forte-boticario-2024')

# Autenticação JWT
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

# Endpoints básicos
@app.route('/')
def home():
    return jsonify({
        "status": "ok",
        "message": "Chatbot Backend está funcionando!",
        "version": "1.0-simple"
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0-simple"
    }), 200

@app.route('/api/auth', methods=['POST'])
def authenticate():
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
            
            return jsonify({
                "status": "success", 
                "token": token
            })
        else:
            return jsonify({"status": "error", "message": "Credenciais inválidas"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/chat', methods=['GET'])
def chat():
    # Verificar token via query parameter
    token = request.args.get('token')
    
    if not token:
        def error_stream():
            yield "data: " + json.dumps({"error": "Token é obrigatório"}) + "\n\n"
        return Response(error_stream(), mimetype='text/event-stream')
    
    try:
        jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
    except:
        def error_stream():
            yield "data: " + json.dumps({"error": "Token inválido"}) + "\n\n"
        return Response(error_stream(), mimetype='text/event-stream')

    pergunta = request.args.get('message', '')
    
    def mock_response():
        yield "data: " + json.dumps({"token": "Olá! "}) + "\n\n"
        yield "data: " + json.dumps({"token": "Esta é uma resposta de teste. "}) + "\n\n"
        yield "data: " + json.dumps({"token": f"Você perguntou: {pergunta}"}) + "\n\n"
        yield "event: end\ndata: \n\n"
    
    return Response(mock_response(), mimetype='text/event-stream')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)