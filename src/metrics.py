from __future__ import annotations

import math
import pandas as pd


def compute_operational_kpis(tickets: pd.DataFrame, jobs: pd.DataFrame) -> dict:
    tickets_total = int(len(tickets))
    backlog = int((tickets["reopen"] == 1).sum()) if "reopen" in tickets.columns else 0
    fcr = float(tickets["fcr"].mean()) * 100 if "fcr" in tickets.columns and tickets_total > 0 else 0.0
    reopen_rate = float(tickets["reopen"].mean()) * 100 if "reopen" in tickets.columns and tickets_total > 0 else 0.0
    ait_mean = float(tickets["ait_min"].mean()) if "ait_min" in tickets.columns and tickets_total > 0 else 0.0
    tnps_mean = float(tickets["tnps"].mean()) if "tnps" in tickets.columns and tickets_total > 0 else 0.0
    jobs_total = int(len(jobs))

    return {
        "tickets_total": tickets_total,
        "backlog": backlog,
        "fcr": fcr,
        "reopen_rate": reopen_rate,
        "ait_mean": ait_mean,
        "tnps_mean": tnps_mean,
        "jobs_total": jobs_total,
    }


def compute_product_kpis(product: pd.DataFrame) -> dict:
    if len(product) == 0:
        return {"conversion_rate": 0.0, "eligibility_rate": 0.0}
    conv_rate = (product["conversions"].sum() / product["applications"].sum()) * 100 if product["applications"].sum() else 0.0
    elig_rate = float(product["eligibility_rate"].mean()) * 100
    return {"conversion_rate": conv_rate, "eligibility_rate": elig_rate}


