#!/usr/bin/env python3
"""
Arquivo principal para Railway - importa a aplicação Flask
"""
import os
import sys

# Adicionar o diretório web_app ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web_app'))

try:
    # Importar a aplicação Flask
    from web_app.app import app
    print("✅ Aplicação Flask importada com sucesso!")
    
except ImportError as e:
    print(f"❌ Erro ao importar aplicação: {e}")
    # Criar uma aplicação de fallback
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def fallback():
        return "Erro: Aplicação principal não pôde ser carregada. Verifique os logs."

# Para desenvolvimento local (não usado em produção)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"🚀 Iniciando Flask app em desenvolvimento na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=True)