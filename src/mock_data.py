from __future__ import annotations

from datetime import datetime, timedelta
import random
import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)


def generate_mock_tickets(days: int = 120) -> pd.DataFrame:
    start = pd.to_datetime(datetime.utcnow().date() - timedelta(days=days))
    rows = []
    categorias = ["Onboarding", "Cobrança", "Cartão", "Consignado", "Crédito", "Outros"]
    canais = ["App", "Chat", "Telefone", "Email"]
    produtos = ["Pessoal", "Cartão", "Consignado"]
    convenios = ["INSS", "SIAPE", "SEDUC", "PM", "OUTROS"]
    ufs = ["SP", "RJ", "MG", "RS", "BA", "PR", "SC", "DF"]
    prioridades = ["Baixa", "Média", "Alta"]

    ticket_id = 1
    for d in pd.date_range(start, periods=days, freq="D"):
        num = np.random.poisson(lam=180)
        for _ in range(num):
            produto = random.choice(produtos)
            convenio = random.choice(convenios) if produto == "Consignado" else None
            ait = max(2, np.random.normal(loc=25 if produto != "Consignado" else 35, scale=10))
            tnps = np.clip(np.random.normal(loc=55 if produto != "Consignado" else 50, scale=15), -100, 100)
            fcr = np.random.rand() < 0.75
            reopen = np.random.rand() < 0.08

            rows.append({
                "ticket_id": ticket_id,
                "timestamp": d + timedelta(minutes=random.randint(0, 24*60-1)),
                "canal": random.choice(canais),
                "produto": produto,
                "convenio": convenio,
                "segmento": random.choice(["PF", "PJ"]),
                "estado": random.choice(ufs),
                "prioridade": random.choice(prioridades),
                "categoria": random.choice(categorias),
                "fcr": 1 if fcr else 0,
                "reopen": 1 if reopen else 0,
                "ait_min": float(ait),
                "tnps": float(tnps),
            })
            ticket_id += 1
    return pd.DataFrame(rows)


def generate_mock_jobs(days: int = 120) -> pd.DataFrame:
    start = pd.to_datetime(datetime.utcnow().date() - timedelta(days=days))
    rows = []
    job_names = ["etl_tickets", "etl_jobs", "agg_product", "train_model", "quality_check"]
    for d in pd.date_range(start, periods=days, freq="D"):
        for job in job_names:
            status = np.random.choice(["SUCCESS", "FAILED", "SKIPPED"], p=[0.9, 0.07, 0.03])
            duration = max(60, int(np.random.normal(loc=600, scale=120)))
            rows.append({
                "job": job,
                "timestamp": d + timedelta(minutes=random.randint(0, 24*60-1)),
                "status": status,
                "duration_s": duration,
            })
    return pd.DataFrame(rows)


def generate_mock_product_metrics(days: int = 120) -> pd.DataFrame:
    start = pd.to_datetime(datetime.utcnow().date() - timedelta(days=days))
    rows = []
    products = ["Pessoal", "Cartão", "Consignado"]
    for d in pd.date_range(start, periods=days, freq="D"):
        for p in products:
            applications = max(10, int(np.random.normal(loc=800 if p != "Consignado" else 350, scale=120)))
            approvals = int(applications * np.clip(np.random.normal(loc=0.55 if p != "Consignado" else 0.45, scale=0.05), 0.1, 0.95))
            conversions = int(approvals * np.clip(np.random.normal(loc=0.6 if p != "Consignado" else 0.5, scale=0.05), 0.1, 0.95))
            eligibility_rate = float(np.clip(np.random.normal(loc=0.7 if p != "Consignado" else 0.6, scale=0.05), 0.2, 0.99))
            rows.append({
                "date": d,
                "product": p,
                "applications": applications,
                "approvals": approvals,
                "conversions": conversions,
                "eligibility_rate": eligibility_rate,
            })
    return pd.DataFrame(rows)


