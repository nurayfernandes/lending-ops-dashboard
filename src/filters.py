from __future__ import annotations

from datetime import date
import pandas as pd

from .data_access import DataSource


def build_filter_options(ds: DataSource) -> dict:
    tickets = ds.tickets.copy()
    tickets["timestamp"] = pd.to_datetime(tickets["timestamp"])  # ensure datetime
    return {
        "min_date": tickets["timestamp"].min().date(),
        "max_date": tickets["timestamp"].max().date(),
        "canal": sorted(tickets["canal"].dropna().unique().tolist()) if "canal" in tickets else [],
        "produto": sorted(tickets["produto"].dropna().unique().tolist()) if "produto" in tickets else [],
        "convenio": sorted(tickets["convenio"].dropna().unique().tolist()) if "convenio" in tickets else [],
        "segmento": sorted(tickets["segmento"].dropna().unique().tolist()) if "segmento" in tickets else [],
        "estado": sorted(tickets["estado"].dropna().unique().tolist()) if "estado" in tickets else [],
        "prioridade": sorted(tickets["prioridade"].dropna().unique().tolist()) if "prioridade" in tickets else [],
        "categoria": sorted(tickets["categoria"].dropna().unique().tolist()) if "categoria" in tickets else [],
    }


def apply_filters(ds: DataSource, filters: dict):
    tickets = ds.tickets.copy()
    jobs = ds.jobs.copy()
    product = ds.product_metrics.copy()

    # Normalizações
    tickets["timestamp"] = pd.to_datetime(tickets["timestamp"])
    jobs["timestamp"] = pd.to_datetime(jobs["timestamp"])
    product["date"] = pd.to_datetime(product["date"]).dt.floor("D")

    start, end = filters["date_range"]
    tickets = tickets[(tickets["timestamp"] >= pd.to_datetime(start)) & (tickets["timestamp"] <= pd.to_datetime(end) + pd.Timedelta(days=1))]
    jobs = jobs[(jobs["timestamp"] >= pd.to_datetime(start)) & (jobs["timestamp"] <= pd.to_datetime(end) + pd.Timedelta(days=1))]
    product = product[(product["date"] >= pd.to_datetime(start)) & (product["date"] <= pd.to_datetime(end))]

    def multi_filter(df: pd.DataFrame, col: str, values: list):
        if col in df.columns and values:
            return df[df[col].isin(values)]
        return df

    tickets = multi_filter(tickets, "canal", filters.get("canal", []))
    tickets = multi_filter(tickets, "produto", filters.get("produto", []))
    tickets = multi_filter(tickets, "convenio", filters.get("convenio", []))
    tickets = multi_filter(tickets, "segmento", filters.get("segmento", []))
    tickets = multi_filter(tickets, "estado", filters.get("estado", []))
    tickets = multi_filter(tickets, "prioridade", filters.get("prioridade", []))
    tickets = multi_filter(tickets, "categoria", filters.get("categoria", []))

    # Produto: filtrar por produto e possivelmente segmento
    product = multi_filter(product, "product", filters.get("produto", []))

    return tickets, jobs, product


