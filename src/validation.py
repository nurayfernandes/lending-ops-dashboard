from __future__ import annotations

from typing import List
import pandas as pd


def run_consistency_checks(tickets: pd.DataFrame, product: pd.DataFrame) -> List[str]:
    issues: List[str] = []

    # Tickets
    if "ait_min" in tickets.columns and (tickets["ait_min"] < 0).any():
        issues.append("Encontrados AIT negativos em tickets.")
    if "tnps" in tickets.columns and ((tickets["tnps"] < -100) | (tickets["tnps"] > 100)).any():
        issues.append("Encontrados tNPS fora do intervalo [-100, 100].")

    # Produto
    if set(["applications","approvals","conversions"]).issubset(product.columns):
        invalid = product[(product["approvals"] > product["applications"]) | (product["conversions"] > product["approvals"])].shape[0]
        if invalid:
            issues.append("Há linhas de produto com conversões>aprovações ou aprovações>aplicações.")

    if "eligibility_rate" in product.columns and ((product["eligibility_rate"] < 0) | (product["eligibility_rate"] > 1)).any():
        issues.append("Encontradas taxas de elegibilidade fora de [0,1].")

    return issues


