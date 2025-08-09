# 🤖 Chatbot de Conhecimento - Grupo Boticário

Sistema de chatbot inteligente para orientação de franqueados do Grupo Boticário, baseado em artigos técnicos e documentação.

## ✅ Correções Realizadas

### 🔧 Problemas Corrigidos:

1. **Servidor de Desenvolvimento em Produção**
   - ❌ **Problema**: Flask estava rodando em modo de desenvolvimento
   - ✅ **Solução**: Configurado Gunicorn para produção

2. **Configuração do Procfile**
   - ❌ **Problema**: Usando `python3 app.py` em produção
   - ✅ **Solução**: Configurado para usar `gunicorn --config gunicorn.conf.py app:app`

3. **Dependências Desatualizadas**
   - ❌ **Problema**: Versões não especificadas causando conflitos
   - ✅ **Solução**: Fixadas versões específicas e estáveis

4. **Tratamento de Erros**
   - ❌ **Problema**: Logs pouco informativos
   - ✅ **Solução**: Implementado logging estruturado com emojis

5. **Configuração de Produção**
   - ❌ **Problema**: Falta de configuração otimizada para produção
   - ✅ **Solução**: Criado `gunicorn.conf.py` com configurações otimizadas

## 🚀 Deploy

### Railway
O projeto está configurado para deploy automático no Railway:

1. **Variáveis de Ambiente Necessárias:**
   ```
   GOOGLE_API_KEY=sua_chave_api_do_google
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=boticario2024
   SECRET_KEY=sua_chave_secreta_muito_forte
   ```

2. **Build Process:**
   - O Railway executa automaticamente o `railway_build.sh`
   - Processa PDFs, limpa dados e cria índice FAISS

3. **Runtime:**
   - Python 3.10.12
   - Gunicorn para produção
   - Configuração otimizada para performance

### Vercel (Frontend)
O frontend está configurado no Vercel e se conecta ao backend do Railway.

## 📁 Estrutura do Projeto

```
javisgb/
├── app.py                 # Ponto de entrada principal
├── requirements.txt       # Dependências Python
├── Procfile              # Configuração do Railway
├── gunicorn.conf.py      # Configuração do Gunicorn
├── railway_build.sh      # Script de build do Railway
├── runtime.txt           # Versão do Python
├── web_app/              # Aplicação Flask
│   ├── app.py           # Servidor Flask principal
│   ├── frontend/        # Frontend React
│   └── *.csv           # Dados processados
├── chatbot/             # Módulo do chatbot
│   └── chatbot.py      # Lógica do chatbot
└── scripts/            # Scripts de processamento
    ├── processar_documentos_pypdf.py
    └── limpar_dados.py
```

## 🔧 Configurações

### Gunicorn (Produção)
- **Workers**: CPU cores × 2 + 1
- **Timeout**: 30 segundos
- **Max Requests**: 1000 por worker
- **Preload App**: True para melhor performance

### Flask (Desenvolvimento)
- **Debug**: False em produção
- **Host**: 0.0.0.0
- **Port**: 5001 (configurável via PORT)

## 📊 Monitoramento

### Endpoints de Saúde
- `GET /` - Status básico
- `GET /health` - Verificação detalhada de saúde

### Logs
- Logs estruturados com emojis para fácil identificação
- Níveis: INFO, WARNING, ERROR
- Captura de erros detalhada

## 🛠️ Desenvolvimento Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar em desenvolvimento
python app.py

# Ou executar diretamente o Flask
cd web_app && python app.py
```

## 🔍 Troubleshooting

### Problemas Comuns:

1. **Chatbot não inicializa**
   - Verificar `GOOGLE_API_KEY`
   - Verificar se os arquivos de índice existem

2. **Erro de importação**
   - Verificar se todas as dependências estão instaladas
   - Verificar versões no `requirements.txt`

3. **Timeout em produção**
   - Ajustar configurações no `gunicorn.conf.py`
   - Verificar recursos do servidor

## 📈 Performance

### Otimizações Implementadas:
- ✅ Gunicorn com múltiplos workers
- ✅ Preload da aplicação
- ✅ Cache do chatbot
- ✅ Streaming de respostas
- ✅ Configurações de timeout otimizadas

### Métricas Esperadas:
- **Tempo de resposta**: < 5 segundos
- **Throughput**: 100+ requests/minuto
- **Uptime**: 99.9%

## 🔐 Segurança

- ✅ CORS configurado para domínios específicos
- ✅ Autenticação JWT
- ✅ Variáveis de ambiente para credenciais
- ✅ Validação de entrada
- ✅ Logs sem informações sensíveis

## 📞 Suporte

Para problemas ou dúvidas:
1. Verificar logs no Railway
2. Testar endpoint `/health`
3. Verificar variáveis de ambiente
4. Consultar documentação técnica

---

**Última atualização**: Agosto 2024
**Versão**: 2.0.0 (Produção Otimizada)