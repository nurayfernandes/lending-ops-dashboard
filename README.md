## Dashboard de Lending (Nubank) – Operação, Produto e Previsões

Este repositório contém um dashboard em Streamlit para análise operacional e de produto de Lending (inclui consignado), com integração opcional ao Databricks. O app oferece filtros por convênios de consignado, canais, produto, segmento, região e outros, além de KPIs, correlações e stubs de modelos preditivos/forecasting.

### Principais funcionalidades
- KPIs de operação: volume de jobs, volume de tickets, SLA, backlog, FCR, reopen rate, AIT, tNPS
- KPIs de produto: conversão, aprovação, elegibilidade, funil
- Filtros: data, canal, produto, convênio (consignado), segmento, estado/região, prioridade e categoria
- Previsões (stubs): séries temporais (volume, AIT, tNPS) e propensão (conversão/eligibilidade)
- Conexão com Databricks (ou uso de dados mockados)

### Pré-requisitos
- Python 3.10+ (recomendado 3.11)

### Instalação
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### Configuração do Databricks (opcional)
Use `st.secrets` do Streamlit (arquivo `.streamlit/secrets.toml`) ou variáveis de ambiente.

Crie o arquivo `.streamlit/secrets.toml` a partir do exemplo:
```toml
# .streamlit/secrets.toml
DATABRICKS_HOST = "https://<sua-instancia>.cloud.databricks.com"
DATABRICKS_HTTP_PATH = "/sql/1.0/warehouses/<http-path>"
DATABRICKS_TOKEN = "dapi-..."

# Nomes de tabelas (ajuste conforme seu catálogo/esquema)
TABLE_TICKETS = "analytics.lending.tickets"
TABLE_JOBS = "analytics.lending.jobs"
TABLE_PRODUCT_METRICS = "analytics.lending.product_metrics"
TABLE_ELIGIBILITY = "analytics.lending.eligibility"

# Gate de autenticação (opcional)
AUTH_ENABLED = true
AUTH_PASSWORD = "defina-uma-senha-forte"
```

Alternativamente, exporte como variáveis de ambiente (útil para CI/CD):
```bash
export DATABRICKS_HOST="https://<sua-instancia>.cloud.databricks.com"
export DATABRICKS_HTTP_PATH="/sql/1.0/warehouses/<http-path>"
export DATABRICKS_TOKEN="dapi-..."
export TABLE_TICKETS="analytics.lending.tickets"
export TABLE_JOBS="analytics.lending.jobs"
export TABLE_PRODUCT_METRICS="analytics.lending.product_metrics"
export TABLE_ELIGIBILITY="analytics.lending.eligibility"
```

Se nenhum segredo/variável for encontrado, o app usará dados mockados automaticamente.

### Executando
```bash
streamlit run streamlit_app.py
```

### Estrutura
```
lending-ops-dashboard/
├── README.md
├── requirements.txt
├── streamlit_app.py
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── databricks_client.py
│   ├── data_access.py
│   ├── mock_data.py
│   ├── metrics.py
│   ├── ml.py
│   ├── ui_components.py
│   └── filters.py
└── .streamlit/
    └── secrets.toml.example
```

### Notas de modelagem preditiva
- As funções de previsão e classificação/regressão são stubs prontos para troca para modelos mais sofisticados (ARIMA/Prophet/XGBoost/AutoML do Databricks). Mantivemos dependências leves e fallback para rodar sem Databricks.

### Segurança e veracidade de dados
- Gate de acesso via senha (`AUTH_ENABLED`, `AUTH_PASSWORD`) usando `st.secrets`.
- Conector Databricks reforçado e mascaramento de credenciais no app.
- Validação de schema com Pandera (`src/schemas.py`) e checagens de consistência (`src/validation.py`).
- Dependências pinadas em `requirements.txt` e dev checks disponíveis em `dev-requirements.txt`.

### Compartilhar no GitHub
Com Git instalado e opcionalmente GitHub CLI (`gh`):
```bash
git init
git add .
git commit -m "chore: scaffold Lending Ops dashboard (Streamlit + Databricks)"
# opcional se usar GitHub CLI e já autenticado:
# gh repo create lending-ops-dashboard --public --source . --remote origin --push
```

### Licença
MIT


