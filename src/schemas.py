from __future__ import annotations

import pandera as pa
from pandera import Column, DataFrameSchema, Check


tickets_schema = DataFrameSchema({
    "ticket_id": Column(int, Check.ge(1)),
    "timestamp": Column(object),
    "canal": Column(str, nullable=True),
    "produto": Column(str, nullable=True),
    "convenio": Column(str, nullable=True),
    "segmento": Column(str, nullable=True),
    "estado": Column(str, nullable=True),
    "prioridade": Column(str, nullable=True),
    "categoria": Column(str, nullable=True),
    "fcr": Column(int, Check.isin([0,1]), nullable=True),
    "reopen": Column(int, Check.isin([0,1]), nullable=True),
    "ait_min": Column(float, Check.ge(0), nullable=True),
    "tnps": Column(float, Check.in_range(-100, 100, include_bounds=True), nullable=True),
}, coerce=True)


jobs_schema = DataFrameSchema({
    "job": Column(str),
    "timestamp": Column(object),
    "status": Column(str, Check.isin(["SUCCESS","FAILED","SKIPPED"])),
    "duration_s": Column(int, Check.ge(0)),
}, coerce=True)


product_schema = DataFrameSchema({
    "date": Column(object),
    "product": Column(str),
    "applications": Column(int, Check.ge(0)),
    "approvals": Column(int, Check.ge(0)),
    "conversions": Column(int, Check.ge(0)),
    "eligibility_rate": Column(float, Check.in_range(0, 1, include_bounds=True)),
}, coerce=True)


