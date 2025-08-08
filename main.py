#!/usr/bin/env python3
"""
Arquivo principal simplificado - apenas importa a aplicação
Railway não deve executar este arquivo diretamente!
"""
from wsgi import app

if __name__ == '__main__':
    print("⚠️ Este arquivo não deve ser executado diretamente!")
    print("⚠️ Use: gunicorn --bind 0.0.0.0:$PORT wsgi:app")
    exit(1)
