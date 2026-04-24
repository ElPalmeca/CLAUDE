"""Script to generate sample reportability data."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

AREAS = [
    "Finanzas", "Operaciones", "Recursos Humanos", "Legal",
    "Tecnología", "Comercial", "Auditoría", "Cumplimiento",
]

TIPOS_REPORTE = [
    "Reporte Mensual", "Reporte Trimestral", "Reporte de Incidencias",
    "Reporte Regulatorio", "Reporte de Gestión", "Reporte Financiero",
    "Reporte de Cumplimiento", "Reporte Operacional",
]

RESPONSABLES = [
    "Ana García", "Carlos López", "María Rodríguez", "Juan Martínez",
    "Laura Sánchez", "Pedro Hernández", "Isabel Fernández", "Diego Torres",
    "Sofía Ramírez", "Andrés Morales", "Valentina Castro", "Felipe Vargas",
]

ESTADOS = ["Aprobado", "Enviado", "En revisión", "Pendiente", "Rechazado"]
ESTADO_WEIGHTS = [0.35, 0.25, 0.20, 0.12, 0.08]

def generate_data(n_rows: int = 500) -> pd.DataFrame:
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)
    date_range = (end_date - start_date).days

    fechas = [start_date + timedelta(days=random.randint(0, date_range)) for _ in range(n_rows)]
    fechas_limite = [f + timedelta(days=random.randint(5, 30)) for f in fechas]
    estados = random.choices(ESTADOS, weights=ESTADO_WEIGHTS, k=n_rows)

    fechas_envio = []
    for i, estado in enumerate(estados):
        if estado in ("Aprobado", "Enviado", "En revisión"):
            dias_adelanto = random.randint(-5, 10)
            fechas_envio.append(fechas_limite[i] - timedelta(days=dias_adelanto))
        elif estado == "Rechazado":
            fechas_envio.append(fechas_limite[i] + timedelta(days=random.randint(1, 5)))
        else:
            fechas_envio.append(None)

    a_tiempo = [
        (fe is not None and fe <= fl)
        for fe, fl in zip(fechas_envio, fechas_limite)
    ]

    df = pd.DataFrame({
        "id": [f"RPT-{str(i+1).zfill(4)}" for i in range(n_rows)],
        "fecha_creacion": [f.date() for f in fechas],
        "fecha_limite": [f.date() for f in fechas_limite],
        "fecha_envio": [f.date() if f else None for f in fechas_envio],
        "area": random.choices(AREAS, k=n_rows),
        "tipo_reporte": random.choices(TIPOS_REPORTE, k=n_rows),
        "estado": estados,
        "responsable": random.choices(RESPONSABLES, k=n_rows),
        "a_tiempo": a_tiempo,
        "observaciones": [
            random.choice(["", "", "", "Requiere revisión adicional", "Información incompleta", "Aprobado con observaciones"])
            for _ in range(n_rows)
        ],
    })

    df = df.sort_values("fecha_creacion").reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = generate_data(500)
    df.to_csv("reportabilidad.csv", index=False)
    df.to_excel("reportabilidad.xlsx", index=False)
    print(f"Generated {len(df)} rows → reportabilidad.csv / reportabilidad.xlsx")
