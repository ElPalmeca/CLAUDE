"""Chart components using Plotly."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config import STATUS_COLORS, STATUS_ORDER


_CHART_CONFIG = {"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]}


def _base_layout(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(
        title={"text": title, "font": {"size": 15}},
        margin={"t": 50, "b": 40, "l": 40, "r": 20},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, sans-serif", "size": 12},
    )
    return fig


def chart_estado_distribucion(df: pd.DataFrame) -> None:
    counts = (
        df["estado"]
        .value_counts()
        .reindex(STATUS_ORDER)
        .dropna()
        .reset_index()
    )
    counts.columns = ["Estado", "Cantidad"]
    colors = [STATUS_COLORS.get(s, "#95a5a6") for s in counts["Estado"]]

    fig = px.bar(
        counts,
        x="Estado",
        y="Cantidad",
        color="Estado",
        color_discrete_map=STATUS_COLORS,
        text="Cantidad",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False)
    _base_layout(fig, "Distribución por Estado")
    st.plotly_chart(fig, use_container_width=True, config=_CHART_CONFIG)


def chart_tendencia_mensual(df: pd.DataFrame) -> None:
    if "fecha_creacion" not in df.columns:
        st.info("Sin datos de fecha para mostrar tendencia.")
        return

    tmp = df.copy()
    tmp["mes"] = pd.to_datetime(tmp["fecha_creacion"]).dt.to_period("M").astype(str)
    monthly = (
        tmp.groupby(["mes", "estado"])
        .size()
        .reset_index(name="cantidad")
    )

    fig = px.area(
        monthly,
        x="mes",
        y="cantidad",
        color="estado",
        color_discrete_map=STATUS_COLORS,
        category_orders={"estado": STATUS_ORDER},
    )
    fig.update_xaxes(tickangle=-30)
    _base_layout(fig, "Tendencia Mensual de Reportes")
    st.plotly_chart(fig, use_container_width=True, config=_CHART_CONFIG)


def chart_por_area(df: pd.DataFrame) -> None:
    area_counts = (
        df.groupby(["area", "estado"])
        .size()
        .reset_index(name="cantidad")
    )

    fig = px.bar(
        area_counts,
        x="cantidad",
        y="area",
        color="estado",
        color_discrete_map=STATUS_COLORS,
        category_orders={"estado": STATUS_ORDER},
        orientation="h",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    _base_layout(fig, "Reportes por Área")
    st.plotly_chart(fig, use_container_width=True, config=_CHART_CONFIG)


def chart_cumplimiento_area(df: pd.DataFrame) -> None:
    if "a_tiempo" not in df.columns:
        return

    tmp = df[df["a_tiempo"].notna()].copy()
    tasa = (
        tmp.groupby("area")["a_tiempo"]
        .apply(lambda s: s.sum() / len(s) * 100)
        .reset_index(name="pct_a_tiempo")
        .sort_values("pct_a_tiempo", ascending=True)
    )

    fig = px.bar(
        tasa,
        x="pct_a_tiempo",
        y="area",
        orientation="h",
        text=tasa["pct_a_tiempo"].apply(lambda v: f"{v:.1f}%"),
        color="pct_a_tiempo",
        color_continuous_scale=["#e74c3c", "#f39c12", "#2ecc71"],
        range_color=[0, 100],
    )
    fig.update_traces(textposition="outside")
    fig.update_coloraxes(showscale=False)
    fig.update_layout(xaxis={"range": [0, 110], "ticksuffix": "%"})
    _base_layout(fig, "% Cumplimiento a Tiempo por Área")
    st.plotly_chart(fig, use_container_width=True, config=_CHART_CONFIG)


def chart_tipo_reporte(df: pd.DataFrame) -> None:
    tipo_counts = df["tipo_reporte"].value_counts().reset_index()
    tipo_counts.columns = ["Tipo", "Cantidad"]

    fig = px.pie(
        tipo_counts,
        names="Tipo",
        values="Cantidad",
        hole=0.45,
    )
    fig.update_traces(textinfo="percent+label", showlegend=False)
    _base_layout(fig, "Distribución por Tipo de Reporte")
    st.plotly_chart(fig, use_container_width=True, config=_CHART_CONFIG)


def chart_responsable_top(df: pd.DataFrame, top_n: int = 10) -> None:
    top = (
        df["responsable"]
        .value_counts()
        .head(top_n)
        .reset_index()
    )
    top.columns = ["Responsable", "Reportes"]

    fig = px.bar(
        top,
        x="Reportes",
        y="Responsable",
        orientation="h",
        text="Reportes",
        color="Reportes",
        color_continuous_scale="Blues",
    )
    fig.update_traces(textposition="outside")
    fig.update_coloraxes(showscale=False)
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    _base_layout(fig, f"Top {top_n} Responsables")
    st.plotly_chart(fig, use_container_width=True, config=_CHART_CONFIG)
