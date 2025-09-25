import os
from datetime import timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import load_databricks_config, is_databricks_configured
from src.data_access import DataSource, load_all_data
from src.metrics import compute_operational_kpis, compute_product_kpis
from src.ml import forecast_series_stub, score_conversion_propensity_stub
from src.filters import apply_filters, build_filter_options
from src.ui_components import kpi_row


st.set_page_config(page_title="Lending Ops & Product Dashboard", layout="wide")


@st.cache_data(show_spinner=False)
def _load_data_cached() -> DataSource:
    cfg = load_databricks_config()
    use_db = is_databricks_configured(cfg)
    return load_all_data(use_databricks=use_db, cfg=cfg)


def _sidebar_filters(ds: DataSource):
    st.sidebar.header("Filtros")
    options = build_filter_options(ds)

    date_range = st.sidebar.date_input(
        "Período",
        value=(options["min_date"], options["max_date"]),
        min_value=options["min_date"],
        max_value=options["max_date"],
    )

    canal = st.sidebar.multiselect("Canal", options["canal"], default=options["canal"])  # type: ignore[index]
    produto = st.sidebar.multiselect("Produto", options["produto"], default=options["produto"])  # type: ignore[index]
    convenio = st.sidebar.multiselect("Convênio (Consignado)", options["convenio"], default=options["convenio"])  # type: ignore[index]
    segmento = st.sidebar.multiselect("Segmento", options["segmento"], default=options["segmento"])  # type: ignore[index]
    estado = st.sidebar.multiselect("UF", options["estado"], default=options["estado"])  # type: ignore[index]
    prioridade = st.sidebar.multiselect("Prioridade", options["prioridade"], default=options["prioridade"])  # type: ignore[index]
    categoria = st.sidebar.multiselect("Categoria Ticket", options["categoria"], default=options["categoria"])  # type: ignore[index]

    return {
        "date_range": date_range,
        "canal": canal,
        "produto": produto,
        "convenio": convenio,
        "segmento": segmento,
        "estado": estado,
        "prioridade": prioridade,
        "categoria": categoria,
    }


def main():
    st.title("Lending – Operação, Produto e Previsões")
    ds = _load_data_cached()
    filters = _sidebar_filters(ds)

    # Filtrar dados
    tickets_f, jobs_f, product_f = apply_filters(ds, filters)

    # KPIs
    op_kpis = compute_operational_kpis(tickets_f, jobs_f)
    prod_kpis = compute_product_kpis(product_f)
    kpi_row({
        "Tickets": op_kpis["tickets_total"],
        "Backlog": op_kpis["backlog"],
        "FCR": f"{op_kpis['fcr']:.1f}%",
        "Reopen": f"{op_kpis['reopen_rate']:.1f}%",
        "AIT (min)": f"{op_kpis['ait_mean']:.1f}",
        "tNPS": f"{op_kpis['tnps_mean']:.1f}",
        "Jobs": op_kpis["jobs_total"],
        "Conversão": f"{prod_kpis['conversion_rate']:.1f}%",
        "Elegibilidade": f"{prod_kpis['eligibility_rate']:.1f}%",
    })

    tab_overview, tab_oper, tab_prod, tab_consignado, tab_prev, tab_src = st.tabs([
        "Visão Geral", "Operação", "Produto", "Consignado", "Previsões", "Fonte"
    ])

    with tab_overview:
        st.subheader("Tendência de Tickets")
        by_day = tickets_f.groupby(pd.Grouper(key="timestamp", freq="D")).size().reset_index(name="tickets")
        if len(by_day) > 0:
            fig = px.line(by_day, x="timestamp", y="tickets")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem dados para o período/filtros selecionados.")

        st.subheader("tNPS e AIT (média por dia)")
        agg = tickets_f.groupby(pd.Grouper(key="timestamp", freq="D")).agg(
            tnps=("tnps", "mean"), ait=("ait_min", "mean")
        ).reset_index()
        fig2 = px.line(agg, x="timestamp", y=["tnps", "ait"], markers=True)
        st.plotly_chart(fig2, use_container_width=True)

    with tab_oper:
        st.subheader("Distribuição por Categoria")
        cat = tickets_f.groupby("categoria").size().reset_index(name="qtd")
        st.plotly_chart(px.bar(cat, x="categoria", y="qtd"), use_container_width=True)

        st.subheader("FCR por Categoria")
        fcr_cat = tickets_f.groupby("categoria").agg(fcr=("fcr", "mean")).reset_index()
        fcr_cat["fcr"] *= 100
        st.plotly_chart(px.bar(fcr_cat, x="categoria", y="fcr"), use_container_width=True)

    with tab_prod:
        st.subheader("Funil: Aplicações → Aprovações → Conversões")
        st.plotly_chart(px.line(product_f.sort_values("date"), x="date", y=["applications", "approvals", "conversions"], markers=True), use_container_width=True)

        st.subheader("Elegibilidade por Produto")
        elig = product_f.groupby("product").agg(rate=("eligibility_rate", "mean")).reset_index()
        elig["rate"] *= 100
        st.plotly_chart(px.bar(elig, x="product", y="rate"), use_container_width=True)

    with tab_consignado:
        st.subheader("KPIs por Convênio")
        conv = tickets_f[tickets_f["produto"] == "Consignado"].groupby("convenio").agg(
            tickets=("ticket_id", "count"),
            tnps=("tnps", "mean"),
            ait=("ait_min", "mean"),
        ).reset_index()
        st.plotly_chart(px.bar(conv, x="convenio", y="tickets"), use_container_width=True)
        st.plotly_chart(px.bar(conv, x="convenio", y="tnps"), use_container_width=True)

    with tab_prev:
        st.subheader("Forecast de Tickets (próximos 14 dias)")
        if 'by_day' in locals() and len(by_day) > 0:
            fc = forecast_series_stub(by_day.set_index("timestamp")["tickets"], horizon=14)
            if len(fc) > 0:
                st.plotly_chart(px.line(fc.reset_index(), x="ds", y=["y", "yhat"], markers=True), use_container_width=True)
            else:
                st.info("Não foi possível gerar forecast com dados vazios.")
        else:
            st.info("Dados insuficientes para forecast.")

        st.subheader("Propensão de Conversão (stub)")
        if len(product_f) > 1:
            demo_features = product_f.tail(30)[["applications", "approvals"]]
            demo_target = product_f.tail(30)["conversions"].gt(0).astype(int)
            scores = score_conversion_propensity_stub(demo_features, demo_target)
            st.write("Distribuição de score (0-1):")
            st.plotly_chart(px.histogram(pd.DataFrame({"score": scores})), use_container_width=True)
        else:
            st.info("Dados insuficientes para estimar propensão de conversão.")

    with tab_src:
        st.write("Fonte de dados em uso:")
        cfg = load_databricks_config()
        if is_databricks_configured(cfg):
            st.success("Databricks (SQL Warehouse)")
            st.code({
                "host": cfg.host,
                "http_path": cfg.http_path,
                "tables": {
                    "tickets": cfg.table_tickets,
                    "jobs": cfg.table_jobs,
                    "product_metrics": cfg.table_product_metrics,
                    "eligibility": cfg.table_eligibility,
                }
            })
        else:
            st.warning("Usando dados mockados (sem credenciais do Databricks)")


if __name__ == "__main__":
    main()


