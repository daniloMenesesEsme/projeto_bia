#!/usr/bin/env python3
"""
SOLUÇÃO DRÁSTICA: Forçar Gunicorn diretamente já que Railway ignora Procfile
"""
import os
import sys
import subprocess

# Se estamos em produção (Railway), forçar Gunicorn
if os.environ.get('PORT') or os.environ.get('RAILWAY_ENVIRONMENT'):
    print("🚀 PRODUÇÃO DETECTADA - FORÇANDO GUNICORN!")
    
    port = os.environ.get('PORT', '5001')
    cmd = [
        'gunicorn', 
        '--bind', f'0.0.0.0:{port}',
        '--workers', '2',
        '--timeout', '30',
        '--access-logfile', '-',
        '--error-logfile', '-',
        'app:app'
    ]
    
    print(f"🔧 Executando: {' '.join(cmd)}")
    
    # Adicionar web_app ao path antes de executar
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web_app'))
    
    # Executar Gunicorn diretamente
    os.execvp('gunicorn', cmd)

# Código para desenvolvimento local e importação
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web_app'))

try:
    from web_app.app import app
    print("✅ Aplicação Flask importada com sucesso!")
except ImportError as e:
    print(f"❌ Erro ao importar aplicação: {e}")
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def fallback():
        return "Erro: Aplicação principal não pôde ser carregada. Verifique os logs."

# Para desenvolvimento local
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"🛠️ Iniciando Flask app em DESENVOLVIMENTO na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=True)