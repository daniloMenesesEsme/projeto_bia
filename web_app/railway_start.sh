#!/bin/bash

# Exibe informações do ambiente
echo "🔍 Verificando ambiente..."
echo "📂 Diretório atual: $(pwd)"
echo "📂 Conteúdo do diretório:"
ls -la

# Verifica se o diretório chatbot existe
if [ -d "chatbot" ]; then
    echo "✅ Diretório chatbot encontrado"
    echo "📂 Conteúdo do diretório chatbot:"
    ls -la chatbot/
else
    echo "⚠️ Diretório chatbot não encontrado, tentando copiar..."
    cp -r ../chatbot .
    if [ -d "chatbot" ]; then
        echo "✅ Diretório chatbot copiado com sucesso"
    else
        echo "❌ Falha ao copiar diretório chatbot"
    fi
fi

# Verifica variáveis de ambiente críticas
echo "🔐 Verificando variáveis de ambiente..."
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️ GOOGLE_API_KEY não encontrada"
else
    echo "✅ GOOGLE_API_KEY configurada"
fi

# Inicia a aplicação
echo "🚀 Iniciando aplicação..."
exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 60