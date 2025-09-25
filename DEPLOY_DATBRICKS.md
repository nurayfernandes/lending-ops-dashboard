## Deploy no Databricks (Lakehouse/Streamlit Apps)

Este guia descreve como publicar o dashboard no Databricks para acesso por nubankers com SSO corporativo.

### Pré-requisitos
- Workspace Databricks com acesso a SQL Warehouse e Unity Catalog (tabelas de Lending)
- Permissão para criar Repos e Apps (ou Notebooks com Streamlit)

### 1) Importar o repositório
1. No Databricks, abra Repos → Add Repo → Import from Git → informe `https://github.com/nurayfernandes/lending-ops-dashboard`
2. Selecione uma branch estável (ex.: `main`) ou uma de PR aprovada

### 2) Configurar segredos
Você pode usar:
- `st.secrets` no Databricks Apps (variáveis do App)
- `dbutils.secrets` com um Secret Scope (arquivo `src/config.py` já tenta ambos)

Variáveis esperadas:
- `DATABRICKS_HOST` (ex.: `https://<workspace>.cloud.databricks.com`)
- `DATABRICKS_HTTP_PATH` (ex.: `/sql/1.0/warehouses/<http-path>`)
- `DATABRICKS_TOKEN` (token do usuário ou service principal com acesso ao warehouse)
- `TABLE_TICKETS`, `TABLE_JOBS`, `TABLE_PRODUCT_METRICS`, `TABLE_ELIGIBILITY`
- Gate opcional: `AUTH_ENABLED=true`, `AUTH_PASSWORD="<senha>"`

Se usar Secret Scope, defina `DATABRICKS_SECRET_SCOPE` como o nome do escopo e crie as chaves acima.

### 3) Criar o App (Lakehouse/Streamlit)
1. Crie um Lakehouse App (ou abra um Notebook e use Streamlit: `streamlit run` inline)
2. Aponte para o arquivo `streamlit_app.py`
3. Defina Secrets/Environment no App (ou use o Secret Scope configurado)
4. Conceda permissão de View/Run aos grupos de nubankers

### 4) Testar e publicar
1. Execute o App e valide filtros, KPIs e abas (inclui “Consignado”)
2. Verifique a aba “Fonte” (credenciais aparecem mascaradas)
3. Caso falte dado/perm, o app cai em mock data automaticamente

### 5) Boas práticas
- Preferir Service Principals com escopos mínimos
- Regras de acesso via Unity Catalog em vez de credenciais por app
- Manter “AUTH_ENABLED=true” se o App for acessível a grupos amplos


