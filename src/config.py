import os
from dataclasses import dataclass

try:
    import streamlit as st
except Exception:  # streamlit not available during static checks
    st = None


@dataclass
class DatabricksConfig:
    host: str | None
    http_path: str | None
    token: str | None
    table_tickets: str | None
    table_jobs: str | None
    table_product_metrics: str | None
    table_eligibility: str | None


def _get_secret(key: str, default: str | None = None) -> str | None:
    # Prefer st.secrets, fallback to env vars
    if st is not None:
        try:
            value = st.secrets.get(key)  # type: ignore[attr-defined]
            if value:
                return str(value)
        except Exception:
            pass
    return os.getenv(key, default)


def load_databricks_config() -> DatabricksConfig:
    return DatabricksConfig(
        host=_get_secret("DATABRICKS_HOST"),
        http_path=_get_secret("DATABRICKS_HTTP_PATH"),
        token=_get_secret("DATABRICKS_TOKEN"),
        table_tickets=_get_secret("TABLE_TICKETS", "analytics.lending.tickets"),
        table_jobs=_get_secret("TABLE_JOBS", "analytics.lending.jobs"),
        table_product_metrics=_get_secret("TABLE_PRODUCT_METRICS", "analytics.lending.product_metrics"),
        table_eligibility=_get_secret("TABLE_ELIGIBILITY", "analytics.lending.eligibility"),
    )


def is_databricks_configured(cfg: DatabricksConfig | None = None) -> bool:
    cfg = cfg or load_databricks_config()
    return bool(cfg.host and cfg.http_path and cfg.token)


