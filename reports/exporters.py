import io
from typing import Any, Dict, Optional

import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False, encoding='utf-8').encode('utf-8')


def df_to_excel_bytes(df: pd.DataFrame, sheet_name: str = 'Reporte') -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return buf.getvalue()


def df_to_pdf_bytes(df: pd.DataFrame, title: str = 'HealthAnalytics IPS - Reporte') -> bytes:
    """PDF simple con tabla truncada (por rendimiento)."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setTitle(title)
    c.setFont('Helvetica-Bold', 14)
    c.drawString(0.75 * inch, height - 0.9 * inch, title)

    c.setFont('Helvetica', 9)

    # Limitar filas para que no explote el PDF
    max_rows = 40
    show_df = df.head(max_rows)

    # Encabezados
    headers = list(show_df.columns)
    x = 0.75 * inch
    y = height - 1.3 * inch

    # Dibujar encabezados
    col_width = (width - 1.5 * inch) / max(1, len(headers))
    for i, h in enumerate(headers):
        c.drawString(x + i * col_width, y, str(h)[:18])

    y -= 0.18 * inch
    # Dibujar filas
    for _, row in show_df.iterrows():
        for i, h in enumerate(headers):
            val = row[h]
            c.drawString(x + i * col_width, y, str(val)[:18])
        y -= 0.18 * inch
        if y < 0.7 * inch:
            c.showPage()
            c.setFont('Helvetica', 9)
            y = height - 1.3 * inch

    c.save()
    return buffer.getvalue()

