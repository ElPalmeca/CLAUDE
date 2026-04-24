"""Tablero de Reportabilidad — Streamlit app."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from config import APP_ICON, APP_LAYOUT, APP_TITLE, BIGQUERY_PROJECT
from components.charts import (
    chart_cumplimiento_area,
    chart_estado_distribucion,
    chart_por_area,
    chart_tendencia_mensual,
    chart_tipo_reporte,
    chart_responsable_top,
)
from components.filters import render_sidebar_filters
from components.kpi_cards import render_kpi_cards
from sources import spreadsheet, bigquery as bq_source
from utils.formatters import apply_filters

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=APP_LAYOUT,
    initial_sidebar_state="expanded",
)

# ── CSS overrides ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    [data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 700; }
    [data-testid="stMetricDelta"] { font-size: 0.8rem; }
    .block-container { padding-top: 1.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title(f"{APP_ICON} {APP_TITLE}")
st.caption("Monitoreo de reportes: estado, cumplimiento y tendencias por área y responsable.")
st.divider()

# ── Data source selector ──────────────────────────────────────────────────────
with st.sidebar:
    st.header("Fuente de Datos")
    source = st.radio(
        "Selecciona la fuente",
        options=["📄 Hoja de Cálculo", "☁️ BigQuery"],
        index=0,
    )

df: pd.DataFrame | None = None
source_error: str | None = None

# ── Load data ─────────────────────────────────────────────────────────────────
if source == "📄 Hoja de Cálculo":
    with st.sidebar:
        st.subheader("Archivo")
        uploaded = st.file_uploader(
            "Sube tu CSV o Excel",
            type=["csv", "xlsx", "xls"],
            help="Columnas requeridas: id, fecha_creacion, fecha_limite, estado, area, tipo_reporte, responsable, a_tiempo",
        )
        use_sample = st.checkbox("Usar datos de ejemplo", value=uploaded is None)

    if uploaded and not use_sample:
        df, errors = spreadsheet.load_uploaded(uploaded)
        if errors:
            source_error = "\n".join(f"• {e}" for e in errors)
    else:
        df = spreadsheet.load_default()

else:  # BigQuery
    with st.sidebar:
        st.subheader("Conexión BigQuery")
        bq_project = st.text_input("Proyecto GCP", value=BIGQUERY_PROJECT)
        bq_dataset = st.text_input("Dataset", value="reportabilidad")
        bq_table = st.text_input("Tabla", value="reportes")
        custom_sql = st.text_area(
            "SQL personalizado (opcional)",
            placeholder="SELECT * FROM `proyecto.dataset.tabla` LIMIT 1000",
            height=120,
        )
        load_bq = st.button("🔄 Cargar desde BigQuery", type="primary", use_container_width=True)

    if load_bq or st.session_state.get("bq_loaded"):
        with st.spinner("Conectando con BigQuery…"):
            df, bq_err = bq_source.load_from_bigquery(
                project=bq_project,
                dataset=bq_dataset,
                table=bq_table,
                custom_query=custom_sql or None,
            )
        if bq_err:
            source_error = bq_err
        else:
            st.session_state["bq_loaded"] = True
    else:
        st.info("Configura la conexión y haz clic en **Cargar desde BigQuery**.")

# ── Error display ─────────────────────────────────────────────────────────────
if source_error:
    st.error(f"**Error al cargar datos:**\n\n{source_error}")
    st.stop()

if df is None:
    st.stop()

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.divider()

filters = render_sidebar_filters(df)
filtered_df = apply_filters(
    df,
    areas=filters["areas"],
    tipos=filters["tipos"],
    estados=filters["estados"],
    responsables=filters["responsables"],
    fecha_inicio=filters["fecha_inicio"],
    fecha_fin=filters["fecha_fin"],
)

if filtered_df.empty:
    st.warning("No hay datos para los filtros seleccionados. Ajusta los filtros en el panel lateral.")
    st.stop()

# ── KPI cards ─────────────────────────────────────────────────────────────────
render_kpi_cards(filtered_df)
st.divider()

# ── Charts — row 1 ────────────────────────────────────────────────────────────
col_left, col_right = st.columns([2, 1])
with col_left:
    chart_tendencia_mensual(filtered_df)
with col_right:
    chart_estado_distribucion(filtered_df)

# ── Charts — row 2 ────────────────────────────────────────────────────────────
col_a, col_b = st.columns(2)
with col_a:
    chart_por_area(filtered_df)
with col_b:
    chart_cumplimiento_area(filtered_df)

# ── Charts — row 3 ────────────────────────────────────────────────────────────
col_c, col_d = st.columns(2)
with col_c:
    chart_tipo_reporte(filtered_df)
with col_d:
    chart_responsable_top(filtered_df)

# ── Data table ────────────────────────────────────────────────────────────────
st.divider()
with st.expander(f"📋 Datos detallados ({len(filtered_df):,} registros)", expanded=False):
    col_search, col_dl = st.columns([3, 1])
    with col_search:
        search = st.text_input("Buscar en tabla", placeholder="ID, responsable, área…")
    with col_dl:
        st.download_button(
            label="⬇️ Descargar CSV",
            data=filtered_df.to_csv(index=False).encode("utf-8"),
            file_name="reportabilidad_filtrado.csv",
            mime="text/csv",
            use_container_width=True,
        )

    display_df = filtered_df
    if search:
        mask = filtered_df.apply(
            lambda col: col.astype(str).str.contains(search, case=False, na=False)
        ).any(axis=1)
        display_df = filtered_df[mask]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": st.column_config.TextColumn("ID"),
            "fecha_creacion": st.column_config.DateColumn("Fecha Creación"),
            "fecha_limite": st.column_config.DateColumn("Fecha Límite"),
            "fecha_envio": st.column_config.DateColumn("Fecha Envío"),
            "a_tiempo": st.column_config.CheckboxColumn("A Tiempo"),
            "estado": st.column_config.TextColumn("Estado"),
            "area": st.column_config.TextColumn("Área"),
            "tipo_reporte": st.column_config.TextColumn("Tipo"),
            "responsable": st.column_config.TextColumn("Responsable"),
            "observaciones": st.column_config.TextColumn("Observaciones"),
        },
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.sidebar.divider()
st.sidebar.caption("Tablero de Reportabilidad · v1.0")
