#!/usr/bin/env python3
"""
Arquivo principal para Railway - importa e executa o app Flask
"""
import os
import sys
import subprocess

def install_requirements():
    """Instala requirements se necessário"""
    try:
        print("🔧 Verificando e instalando dependências...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependências instaladas com sucesso!")
            print(f"Saída: {result.stdout}")
        else:
            print(f"⚠️ Problema na instalação de dependências:")
            print(f"Saída: {result.stdout}")
            print(f"Erro: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Erro ao instalar dependências: {e}")

if __name__ == '__main__':
    # Instalar dependências primeiro
    install_requirements()
    
    # Adicionar o diretório web_app ao path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web_app'))
    
    try:
        # Importar e executar a aplicação
        from web_app.app import app
        
        port = int(os.environ.get('PORT', 5001))
        print(f"🚀 Iniciando Flask app na porta {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    except ImportError as e:
        print(f"❌ Erro ao importar aplicação: {e}")
        # Tentar executar diretamente
        os.system(f"cd web_app && python3 app.py")