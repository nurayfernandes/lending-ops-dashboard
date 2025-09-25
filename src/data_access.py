from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import pandas as pd

from .config import DatabricksConfig
from .databricks_client import run_query
from .mock_data import generate_mock_tickets, generate_mock_jobs, generate_mock_product_metrics
from .schemas import tickets_schema, jobs_schema, product_schema


@dataclass
class DataSource:
    tickets: pd.DataFrame
    jobs: pd.DataFrame
    product_metrics: pd.DataFrame


def load_all_data(use_databricks: bool, cfg: Optional[DatabricksConfig] = None) -> DataSource:
    if use_databricks:
        # Expecting table names in cfg
        assert cfg is not None
        tickets = run_query(f"SELECT * FROM {cfg.table_tickets}")
        jobs = run_query(f"SELECT * FROM {cfg.table_jobs}")
        product = run_query(f"SELECT * FROM {cfg.table_product_metrics}")

        # Normalize column names/time
        if "timestamp" in tickets.columns:
            tickets["timestamp"] = pd.to_datetime(tickets["timestamp"])
        if "timestamp" in jobs.columns:
            jobs["timestamp"] = pd.to_datetime(jobs["timestamp"])
        if "date" in product.columns:
            product["date"] = pd.to_datetime(product["date"]).dt.date
            product["date"] = pd.to_datetime(product["date"])  # standardize to datetime
        # Validate schemas
        tickets = tickets_schema.validate(tickets, lazy=True)
        jobs = jobs_schema.validate(jobs, lazy=True)
        product = product_schema.validate(product, lazy=True)
        return DataSource(tickets=tickets, jobs=jobs, product_metrics=product)

    # Fallback: mock data
    tickets = generate_mock_tickets()
    jobs = generate_mock_jobs()
    product = generate_mock_product_metrics()
    # Validate schemas for mock as well
    tickets = tickets_schema.validate(tickets, lazy=True)
    jobs = jobs_schema.validate(jobs, lazy=True)
    product = product_schema.validate(product, lazy=True)
    return DataSource(tickets=tickets, jobs=jobs, product_metrics=product)


