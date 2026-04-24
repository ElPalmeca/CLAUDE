"""Spreadsheet data source: CSV and Excel."""
import pandas as pd
import streamlit as st
from pathlib import Path


REQUIRED_COLUMNS = {
    "id", "fecha_creacion", "fecha_limite", "estado", "area",
    "tipo_reporte", "responsable", "a_tiempo",
}

DATE_COLUMNS = ["fecha_creacion", "fecha_limite", "fecha_envio"]


def _coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
    if "a_tiempo" in df.columns:
        df["a_tiempo"] = df["a_tiempo"].map(
            lambda v: True if str(v).lower() in ("true", "1", "sí", "si", "yes") else False
        )
    return df


def _validate(df: pd.DataFrame) -> list[str]:
    missing = REQUIRED_COLUMNS - set(df.columns)
    return [f"Columna requerida faltante: '{c}'" for c in missing]


def load_default() -> pd.DataFrame:
    """Load the bundled sample CSV."""
    path = Path(__file__).parent.parent / "data" / "reportabilidad.csv"
    df = pd.read_csv(path)
    return _coerce_types(df)


def load_uploaded(uploaded_file) -> tuple[pd.DataFrame | None, list[str]]:
    """Parse a user-uploaded CSV or Excel file.

    Returns (dataframe, errors). If errors is non-empty the dataframe is None.
    """
    name = uploaded_file.name.lower()
    try:
        if name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        else:
            return None, ["Formato no soportado. Use CSV o Excel (.xlsx/.xls)."]
    except Exception as exc:
        return None, [f"Error al leer el archivo: {exc}"]

    errors = _validate(df)
    if errors:
        return None, errors

    return _coerce_types(df), []
