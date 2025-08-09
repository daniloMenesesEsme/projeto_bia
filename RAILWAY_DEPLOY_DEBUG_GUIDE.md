# Guia de Depuração de Deploy no Railway para Projeto de Chatbot

Este documento resume os problemas encontrados e as soluções aplicadas durante o processo de deploy do projeto de chatbot no Railway. Ele serve como um guia de referência para futuras depurações e como um registro de aprendizado.

---

## Sumário dos Problemas e Soluções

### 1. Erro: `Nixpacks was unable to generate a build plan for this app.`
   - **Causa Raiz:** O Railway (usando Nixpacks) não conseguia identificar o tipo de projeto devido à estrutura do repositório (muitos arquivos e pastas na raiz, além do `web_app` principal) e/ou configurações incorretas de `rootDirectory`.
   - **Solução:**
     - **Remoção de Conflitos:** Excluídos `Procfile` e `railway.toml` de `web_app/` e da raiz do projeto para evitar conflitos.
     - **Introdução de `Dockerfile`:** Criado um `Dockerfile` na **raiz do repositório** para fornecer um processo de build explícito, ignorando a detecção automática do Nixpacks.
     - **Configuração Crucial na UI do Railway:**
       - **Settings > Source > Root Directory:** Definido como **`/`** (a raiz do repositório). Isso garante que o Railway veja o `Dockerfile` e o contexto de build correto.
       - **Settings > Build > Builder (ou Build Type):** Deixado para auto-detecção (o Railway detecta o `Dockerfile` na raiz).
     - **Ajuste do `Dockerfile`:** O `Dockerfile` foi modificado para copiar explicitamente o conteúdo da pasta `web_app` para a raiz do diretório de trabalho do contêiner (`/app`).
       ```dockerfile
       FROM python:3.9-slim-buster

       WORKDIR /app

       # Copia o requirements.txt da pasta web_app
       COPY web_app/requirements.txt ./requirements.txt
       RUN pip install --no-cache-dir -r requirements.txt

       # Copia todo o conteúdo da pasta web_app para o /app do contêiner
       COPY web_app/ .

       CMD ["python", "app.py"]
       ```

### 2. Erro: `ModuleNotFoundError: No module named 'app_simple'` ou `No module named 'web_app'`
   - **Causa Raiz:** O Gunicorn (servidor web) não conseguia encontrar o módulo da aplicação Flask (`app.py`) devido a um caminho incorreto no comando de inicialização.
   - **Solução:**
     - **Ajuste do `startCommand`:** O comando de inicialização em `railway.toml` (e confirmado na UI do Railway) foi alterado para refletir a estrutura do aplicativo dentro do contêiner Docker.
       - **Settings > Deploy > Custom Start Command:** Definido como **`sh -c "gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 60 app:app"`**.
       - Isso garante que o Gunicorn procure por `app.py` diretamente na raiz do diretório de trabalho do contêiner (`/app`), onde o `Dockerfile` o copiou.

### 3. Erro: `Starting Container Error: '$PORT' is not a valid port number.`
   - **Causa Raiz:** A variável de ambiente `$PORT` não estava sendo expandida corretamente pelo shell antes de ser passada para o Gunicorn.
   - **Solução:**
     - **Uso de `sh -c`:** O `startCommand` foi envolvido em `sh -c "..."` para forçar a expansão da variável de ambiente pelo shell.
       - **Settings > Deploy > Custom Start Command:** Definido como **`sh -c "gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 60 app:app"`**.

### 4. Erro: `SyntaxError: closing parenthesis '}' does not match opening parenthesis '('`
   - **Causa Raiz:** Um erro de sintaxe no código Python (`web_app/app.py`, linha 50) devido a um parêntese/chave extra.
   - **Solução:**
     - **Correção do Código:** Removido o caractere `}` extra na linha 50 de `web_app/app.py`.
       - Linha original: `yield "data: " + json.dumps({"answer": "Serviço em manutenção. Por favor, tente novamente mais tarde."}}) + "\n\n"`
       - Linha corrigida: `yield "data: " + json.dumps({"answer": "Serviço em manutenção. Por favor, tente novamente mais tarde."}) + "\n\n"`

### 5. Problema: `requirements.txt` não encontrado na raiz
   - **Causa Raiz:** O `app.py` na raiz do projeto tentava instalar dependências de um `requirements.txt` que estava em `web_app/`.
   - **Solução:**
     - **Ajuste do `app.py` (raiz):** Modificado o `app.py` na raiz para apontar corretamente para `web_app/requirements.txt` durante a instalação de dependências.

### 6. Problema: Processamento de Dados Ausente na Inicialização
   - **Causa Raiz:** A função `verificar_e_processar_dados` em `web_app/app.py` verificava a existência do índice FAISS, mas não o criava se estivesse ausente.
   - **Solução:**
     - **Chamada Explícita da Função:** Modificado `web_app/app.py` para chamar `criar_e_salvar_indice_estruturado()` se o índice não fosse encontrado.

---

## Lições Aprendidas e Pontos Chave para o Futuro

*   **Configurações da UI do Railway são Primordiais:** As configurações feitas diretamente na interface do Railway (especialmente "Root Directory" e "Custom Start Command") podem e geralmente **substituem** as configurações em `railway.toml`. Sempre verifique a UI primeiro.
*   **`Dockerfile` para Controle Explícito:** Em projetos com estruturas complexas ou quando a detecção automática falha, um `Dockerfile` é a maneira mais robusta de definir o ambiente de build e execução.
*   **Contexto de Build do Dockerfile:** Os caminhos dentro do `Dockerfile` são relativos ao "Root Directory" definido na UI do Railway. Se o "Root Directory" for `/`, o `Dockerfile` deve lidar com a cópia de subdiretórios (como `web_app/`) explicitamente.
*   **Comandos de Inicialização do Gunicorn:** O formato `gunicorn module:app_object` é padrão. Certifique-se de que `module` e `app_object` correspondam exatamente ao caminho e nome do objeto da aplicação Flask dentro do ambiente do contêiner.
*   **Expansão de Variáveis de Ambiente:** Para garantir que variáveis como `$PORT` sejam expandidas corretamente em comandos de inicialização, envolva o comando em `sh -c "..."`.
*   **Depuração Iterativa:** Problemas de deploy raramente são resolvidos com uma única alteração. É um processo iterativo de identificar um erro, aplicar uma correção, e então depurar o próximo erro que surgir.
*   **Limpeza do Repositório:** Manter o repositório limpo e organizado (evitando arquivos de backup ou configurações antigas na raiz) pode prevenir muitos problemas de detecção automática.

---

Este guia deve ser um recurso valioso para futuras depurações.
