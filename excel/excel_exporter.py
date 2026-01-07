#excel.excel_exporter

import openpyxl
from openpyxl.styles import PatternFill, Font
import os
from datetime import datetime
from dotenv import load_dotenv
import subprocess
import platform

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

    start_row = 19  # fila inicial B19
    start_col = 2   # columna B

    current_row = start_row

    # estilos
    default_font = Font(name="Calibri", size=12, bold=True)
    title_fill = PatternFill(start_color="0000FF", end_color="0000FF", fill_type="solid")
    title_font = Font(name="Calibri", size=12, color="FFFFFF", bold=True)

    for row in model.rows:
        if row.type == "PRODUCT":
            cells = [
                (row.col_1, start_col),       # nombre producto
                (row.col_2, start_col + 1),   # cantidad
                (row.col_3, start_col + 2),   # precio unitario
                (row.col_4, start_col + 3)    # total
            ]
            for value, col in cells:
                cell = ws.cell(row=current_row, column=col, value=value)
                cell.font = default_font
            current_row += 1

        elif row.type == "TITLE":
            cell = ws.cell(row=current_row, column=start_col, value=row.col_1)
            cell.fill = title_fill
            cell.font = title_font
            current_row += 1

        elif row.type == "INFO":
            cells = [
                (row.col_1, start_col),       # info col1 en B
                (row.col_2, start_col + 1)    # info col2 en C
            ]
            for value, col in cells:
                cell = ws.cell(row=current_row, column=col, value=value)
                cell.font = default_font
            current_row += 1

        elif row.type == "EMPTY":
            current_row += 1

    wb.save(output_path)

    # abrir el archivo automáticamente
    try:
        if platform.system() == "Windows":
            os.startfile(output_path)
        elif platform.system() == "Darwin":
            subprocess.call(["open", output_path])
        else:  # Linux
            subprocess.call(["xdg-open", output_path])
    except Exception as e:
        print(f"No se pudo abrir automáticamente el archivo: {e}")

    return output_path

