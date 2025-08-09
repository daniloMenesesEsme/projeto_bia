# Resumo das Atividades de Deploy - Projeto BIA

## 1. Deploy no Vercel (Frontend)
- Configuração do projeto no Vercel
- Diretório raiz: `web_app/frontend`
- Build Command: `npm run build`
- Output Directory: `build`
- Deploy realizado com sucesso

## 2. Deploy no Railway (Backend)
### Etapas Realizadas:
1. **Organização da Estrutura do Projeto**
   - Remoção de arquivos duplicados
   - Centralização dos arquivos de configuração em `web_app/`
   - Configuração do Root Directory como `web_app`

2. **Configuração dos Arquivos**
   - **railway.toml**:
     ```toml
     [build]
     builder = "nixpacks"
     buildCommand = "pip install -r requirements.txt"

     [deploy]
     startCommand = "gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 60"
     healthcheckPath = "/"
     healthcheckTimeout = 100
     ```

   - **Procfile**:
     ```
     web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 60
     ```

   - **requirements.txt**:
     ```
     Flask>=2.3.0
     Flask-Cors>=4.0.0
     gunicorn>=21.0.0
     python-dotenv>=1.0.0
     numpy>=1.24.0
     pandas>=2.0.0
     scikit-learn>=1.0.0
     faiss-cpu>=1.7.0
     PyPDF2>=3.0.0
     python-magic>=0.4.27
     tqdm>=4.65.0
     ```

3. **Variáveis de Ambiente Configuradas**
   ```
   PORT=5000
   FLASK_ENV=production
   CORS_ORIGIN=https://projeto-bia.vercel.app
   PYTHONPATH=/web_app
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=boticario2024
   ```

4. **Correções de Problemas**
   - Resolvido problema de estrutura de diretórios
   - Corrigido encoding do Procfile para UTF-8
   - Removidas configurações inválidas do railway.toml

## 3. Comandos Git Utilizados
```bash
# Remoção de arquivos duplicados
git add .
git commit -m "fix: reorganiza estrutura do projeto e remove arquivos duplicados"
git push origin main

# Correção do Procfile
Set-Content -Path "web_app/Procfile" -Value "web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 60" -Encoding UTF8
git add web_app/Procfile
git commit -m "fix: recria Procfile com encoding UTF-8 correto"
git push origin main
```

## 4. URLs dos Serviços
- Frontend: https://projeto-bia.vercel.app
- Backend: https://web-production-a660a.up.railway.app

## Próximos Passos
1. Monitorar o deploy no Railway
2. Testar a integração entre frontend e backend
3. Verificar logs de produção para possíveis ajustes
4. Implementar monitoramento de erros