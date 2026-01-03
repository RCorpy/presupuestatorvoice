# excel/excel_exporter.py
import openpyxl
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BASE_EXCEL = os.getenv("EXCEL_BASE_PATH", "base.xlsx")
OUTPUT_DIR = os.getenv("EXCEL_OUTPUT_DIR", "output")


def export_proforma_to_excel(model):
    if not os.path.exists(BASE_EXCEL):
        raise FileNotFoundError(f"No se encuentra el Excel base: {BASE_EXCEL}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(
        OUTPUT_DIR,
        f"proforma_{timestamp}.xlsx"
    )

    wb = openpyxl.load_workbook(BASE_EXCEL)
    ws = wb.active

    start_row = 2  # encabezados en fila 1

    for i, row in enumerate(model.data, start=start_row):
        ws.cell(row=i, column=1, value=row.get("producto"))
        ws.cell(row=i, column=2, value=row.get("cantidad"))
        ws.cell(row=i, column=3, value=row.get("precio"))
        ws.cell(row=i, column=4, value=row.get("total"))

    wb.save(output_path)
    return output_path
