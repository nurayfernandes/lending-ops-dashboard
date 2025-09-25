from __future__ import annotations

import streamlit as st


def kpi_row(kpis: dict):
    cols = st.columns(len(kpis))
    for col, (label, value) in zip(cols, kpis.items()):
        with col:
            st.metric(label, value)


