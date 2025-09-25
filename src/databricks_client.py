from __future__ import annotations

import contextlib
from typing import Any, Dict, Iterable, Optional

import pandas as pd

from .config import DatabricksConfig, load_databricks_config, is_databricks_configured


def _connect(cfg: Optional[DatabricksConfig] = None):
    cfg = cfg or load_databricks_config()
    if not is_databricks_configured(cfg):
        raise RuntimeError("Databricks não configurado. Defina DATABRICKS_HOST, DATABRICKS_HTTP_PATH e DATABRICKS_TOKEN.")

    from databricks import sql  # lazy import

    return sql.connect(
        server_hostname=str(cfg.host),
        http_path=str(cfg.http_path),
        access_token=str(cfg.token),
        _user_agent_entry="lending-ops-dashboard/1.0",
    )


def run_query(sql_text: str, params: Optional[Dict[str, Any]] = None, cfg: Optional[DatabricksConfig] = None) -> pd.DataFrame:
    """Executa uma consulta SQL em um SQL Warehouse do Databricks e retorna um DataFrame.

    Observação: parâmetros são interpolados pelo conector (se suportado) ou por formatação simples.
    Evite passar entradas de usuário diretamente. Aqui mantemos simples com format().
    """
    cfg = cfg or load_databricks_config()
    if not is_databricks_configured(cfg):
        raise RuntimeError("Databricks não configurado.")

    formatted_sql = sql_text
    if params:
        formatted_sql = sql_text.format(**{k: _format_sql_value(v) for k, v in params.items()})

    with contextlib.closing(_connect(cfg)) as conn:
        with contextlib.closing(conn.cursor()) as cur:
            # Disallow multiple statements and enforce simple queries
            if ";" in formatted_sql.strip().rstrip(";"):
                raise ValueError("SQL com múltiplos statements não é permitido.")
            cur.execute(formatted_sql)
            rows = cur.fetchall()
            cols = [c[0] for c in cur.description]
            return pd.DataFrame.from_records(rows, columns=cols)


def _format_sql_value(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        # quote each
        return ",".join(_format_sql_value(v) for v in value)
    # default: quote string
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


