"""KPI metric cards component."""
import streamlit as st
from utils.formatters import compute_kpis, pct


def render_kpi_cards(df) -> None:
    kpis = compute_kpis(df)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="Total Reportes",
            value=f"{kpis['total']:,}",
        )
    with col2:
        st.metric(
            label="Aprobados",
            value=f"{kpis['aprobados']:,}",
            delta=pct(kpis["tasa_aprobacion"]) + " aprobación",
        )
    with col3:
        st.metric(
            label="Pendientes",
            value=f"{kpis['pendientes']:,}",
            delta=f"{kpis['pendientes']} sin enviar",
            delta_color="inverse",
        )
    with col4:
        st.metric(
            label="Rechazados",
            value=f"{kpis['rechazados']:,}",
            delta_color="inverse",
        )
    with col5:
        st.metric(
            label="Enviados a Tiempo",
            value=pct(kpis["tasa_a_tiempo"]),
            delta="del total enviado",
        )
