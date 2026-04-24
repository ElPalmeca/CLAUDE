"""Sidebar filters component."""
from __future__ import annotations

import pandas as pd
import streamlit as st


def render_sidebar_filters(df: pd.DataFrame) -> dict:
    st.sidebar.header("Filtros")

    fecha_min = pd.to_datetime(df["fecha_creacion"]).min().date()
    fecha_max = pd.to_datetime(df["fecha_creacion"]).max().date()

    col_fi, col_ff = st.sidebar.columns(2)
    with col_fi:
        fecha_inicio = st.date_input("Desde", value=fecha_min, min_value=fecha_min, max_value=fecha_max)
    with col_ff:
        fecha_fin = st.date_input("Hasta", value=fecha_max, min_value=fecha_min, max_value=fecha_max)

    areas = st.sidebar.multiselect(
        "Área",
        options=sorted(df["area"].dropna().unique()),
    )

    tipos = st.sidebar.multiselect(
        "Tipo de Reporte",
        options=sorted(df["tipo_reporte"].dropna().unique()),
    )

    estados = st.sidebar.multiselect(
        "Estado",
        options=sorted(df["estado"].dropna().unique()),
    )

    responsables = st.sidebar.multiselect(
        "Responsable",
        options=sorted(df["responsable"].dropna().unique()),
    )

    st.sidebar.divider()
    st.sidebar.caption(f"Total registros: **{len(df):,}**")

    return {
        "areas": areas or None,
        "tipos": tipos or None,
        "estados": estados or None,
        "responsables": responsables or None,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
    }
