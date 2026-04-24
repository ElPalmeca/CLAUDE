"""Utility functions for formatting and filtering data."""
from __future__ import annotations

import pandas as pd


def pct(value: float, decimals: int = 1) -> str:
    return f"{value:.{decimals}f}%"


def delta_arrow(value: float) -> str:
    if value > 0:
        return f"▲ {pct(value)}"
    if value < 0:
        return f"▼ {pct(abs(value))}"
    return "— sin cambio"


def apply_filters(
    df: pd.DataFrame,
    areas: list[str] | None,
    tipos: list[str] | None,
    estados: list[str] | None,
    responsables: list[str] | None,
    fecha_inicio,
    fecha_fin,
) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)

    if areas:
        mask &= df["area"].isin(areas)
    if tipos:
        mask &= df["tipo_reporte"].isin(tipos)
    if estados:
        mask &= df["estado"].isin(estados)
    if responsables:
        mask &= df["responsable"].isin(responsables)
    if fecha_inicio and "fecha_creacion" in df.columns:
        mask &= pd.to_datetime(df["fecha_creacion"]) >= pd.Timestamp(fecha_inicio)
    if fecha_fin and "fecha_creacion" in df.columns:
        mask &= pd.to_datetime(df["fecha_creacion"]) <= pd.Timestamp(fecha_fin)

    return df[mask].copy()


def compute_kpis(df: pd.DataFrame) -> dict:
    total = len(df)
    aprobados = (df["estado"] == "Aprobado").sum()
    pendientes = (df["estado"] == "Pendiente").sum()
    rechazados = (df["estado"] == "Rechazado").sum()
    enviados_ok = df["a_tiempo"].sum() if "a_tiempo" in df.columns else 0
    enviados_total = df["a_tiempo"].notna().sum() if "a_tiempo" in df.columns else 0

    return {
        "total": int(total),
        "aprobados": int(aprobados),
        "pendientes": int(pendientes),
        "rechazados": int(rechazados),
        "tasa_aprobacion": (aprobados / total * 100) if total else 0,
        "tasa_a_tiempo": (enviados_ok / enviados_total * 100) if enviados_total else 0,
    }
