#!/usr/bin/env python3
"""
Arquivo principal para Railway - importa a aplicação Flask
IMPORTANTE: Este arquivo NÃO deve ser executado diretamente em produção!
Use o Procfile: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 30 app:app
"""
import os
import sys

# Adicionar o diretório web_app ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web_app'))

try:
    # Importar a aplicação Flask
    from web_app.app import app
    print("✅ Aplicação Flask importada com sucesso!")
    
    # FORÇAR GUNICORN EM PRODUÇÃO
    if os.environ.get('RAILWAY_ENVIRONMENT') == 'production' or os.environ.get('PORT'):
        print("🚨 ERRO: Não execute este arquivo diretamente em produção!")
        print("🚨 Use o Procfile: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 30 app:app")
        print("🚨 Railway deve usar o Procfile, não python app.py")
        sys.exit(1)
    
except ImportError as e:
    print(f"❌ Erro ao importar aplicação: {e}")
    # Criar uma aplicação de fallback
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def fallback():
        return "Erro: Aplicação principal não pôde ser carregada. Verifique os logs."

# Para desenvolvimento local APENAS
if __name__ == '__main__':
    if os.environ.get('RAILWAY_ENVIRONMENT') == 'production':
        print("🚨 NÃO EXECUTE EM PRODUÇÃO! Use Gunicorn via Procfile!")
        sys.exit(1)
        
    port = int(os.environ.get('PORT', 5001))
    print(f"🛠️ Iniciando Flask app em DESENVOLVIMENTO na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=True)