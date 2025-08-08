#!/bin/bash

# Para a execução se qualquer comando falhar
set -e

echo "🚀 BUILD_START: Instalando dependências..."
pip install -r requirements.txt

echo "📄 BUILD_STEP: Processando PDFs para criar base_conhecimento.csv..."
if python scripts/processar_documentos_pypdf.py; then
    echo "✅ PDFs processados com sucesso!"
else
    echo "⚠️ Aviso: Erro ao processar PDFs, continuando..."
fi

echo "🧹 BUILD_STEP: Limpando base_conhecimento.csv..."
if python scripts/limpar_dados.py; then
    echo "✅ Dados limpos com sucesso!"
else
    echo "⚠️ Aviso: Erro ao limpar dados, continuando..."
fi

echo "🔍 BUILD_STEP: Criando o índice FAISS estruturado..."
if python web_app/criar_indice_estruturado.py; then
    echo "✅ Índice FAISS criado com sucesso!"
else
    echo "⚠️ Aviso: Erro ao criar índice FAISS, continuando..."
fi

echo "✅ BUILD_COMPLETE: Build concluído!"
echo "🚀 Aplicação pronta para deploy no Railway!"
