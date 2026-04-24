import os
from dotenv import load_dotenv

load_dotenv()

BIGQUERY_PROJECT = os.getenv("BIGQUERY_PROJECT", "")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET", "reportabilidad")
BIGQUERY_TABLE = os.getenv("BIGQUERY_TABLE", "reportes")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

APP_TITLE = "Tablero de Reportabilidad"
APP_ICON = "📊"
APP_LAYOUT = "wide"

STATUS_COLORS = {
    "Aprobado": "#2ecc71",
    "Enviado": "#3498db",
    "En revisión": "#f39c12",
    "Pendiente": "#e67e22",
    "Rechazado": "#e74c3c",
}

STATUS_ORDER = ["Aprobado", "Enviado", "En revisión", "Pendiente", "Rechazado"]
