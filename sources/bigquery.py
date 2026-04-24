"""BigQuery data source."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from config import BIGQUERY_PROJECT, BIGQUERY_DATASET, BIGQUERY_TABLE


_DEFAULT_QUERY = """
SELECT
    id,
    DATE(fecha_creacion)   AS fecha_creacion,
    DATE(fecha_limite)     AS fecha_limite,
    DATE(fecha_envio)      AS fecha_envio,
    area,
    tipo_reporte,
    estado,
    responsable,
    a_tiempo,
    observaciones
FROM `{project}.{dataset}.{table}`
ORDER BY fecha_creacion DESC
"""


def _get_client():
    try:
        from google.cloud import bigquery
        return bigquery.Client(project=BIGQUERY_PROJECT)
    except ImportError:
        raise RuntimeError(
            "google-cloud-bigquery no está instalado. "
            "Ejecuta: pip install google-cloud-bigquery"
        )
    except Exception as exc:
        raise RuntimeError(f"No se pudo conectar a BigQuery: {exc}") from exc


@st.cache_data(ttl=300, show_spinner=False)
def load_from_bigquery(
    project: str = BIGQUERY_PROJECT,
    dataset: str = BIGQUERY_DATASET,
    table: str = BIGQUERY_TABLE,
    custom_query: str | None = None,
) -> tuple[pd.DataFrame | None, str | None]:
    """Fetch data from BigQuery.

    Returns (dataframe, error_message). On success error_message is None.
    Cache TTL is 5 minutes.
    """
    if not project:
        return None, "BIGQUERY_PROJECT no configurado. Revisa el archivo .env"

    try:
        client = _get_client()
        query = custom_query or _DEFAULT_QUERY.format(
            project=project, dataset=dataset, table=table
        )
        df = client.query(query).to_dataframe()
        for col in ["fecha_creacion", "fecha_limite", "fecha_envio"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
        return df, None
    except Exception as exc:
        return None, str(exc)


def build_custom_query(
    project: str,
    dataset: str,
    table: str,
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None,
    areas: list[str] | None = None,
) -> str:
    """Build a parameterized BigQuery SQL query."""
    conditions = []
    if fecha_inicio:
        conditions.append(f"DATE(fecha_creacion) >= '{fecha_inicio}'")
    if fecha_fin:
        conditions.append(f"DATE(fecha_creacion) <= '{fecha_fin}'")
    if areas:
        quoted = ", ".join(f"'{a}'" for a in areas)
        conditions.append(f"area IN ({quoted})")

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    return f"""
SELECT
    id,
    DATE(fecha_creacion)   AS fecha_creacion,
    DATE(fecha_limite)     AS fecha_limite,
    DATE(fecha_envio)      AS fecha_envio,
    area,
    tipo_reporte,
    estado,
    responsable,
    a_tiempo,
    observaciones
FROM `{project}.{dataset}.{table}`
{where}
ORDER BY fecha_creacion DESC
"""
