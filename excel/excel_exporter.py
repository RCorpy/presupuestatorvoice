# excel/excel_exporter.py

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

    # ─────────────────────────────
    # Posición inicial (B19)
    # ─────────────────────────────
    start_row = 19
    start_col = 2  # columna B
    current_row = start_row

    # ─────────────────────────────
    # Estilos
    # ─────────────────────────────
    default_font = Font(name="Calibri", size=12, bold=True)

    title_fill = PatternFill(
        start_color="0000FF",
        end_color="0000FF",
        fill_type="solid"
    )
    title_font = Font(
        name="Calibri",
        size=12,
        color="FFFFFF",
        bold=True
    )

    # ─────────────────────────────
    # Render filas
    # ─────────────────────────────
    for row in model.rows:

        # =========================
        # TITLE
        # =========================
        if row.type == "TITLE":
            ws.merge_cells(
                start_row=current_row,
                start_column=start_col,
                end_row=current_row,
                end_column=start_col + 4
            )

            cell = ws.cell(
                row=current_row,
                column=start_col,
                value=row.col_0
            )
            cell.fill = title_fill
            cell.font = title_font

            current_row += 1

        # =========================
        # PRODUCT
        # =========================
        elif row.type == "PRODUCT":
            if float(row.col_2) > 0:
                # B → Kits
                ws.cell(
                    row=current_row,
                    column=start_col,
                    value=row.col_0
                ).font = default_font

                # C → Producto
                ws.cell(
                    row=current_row,
                    column=start_col + 1,
                    value=row.col_1
                ).font = default_font

                # D → Cantidad
                qty_cell = ws.cell(
                    row=current_row,
                    column=start_col + 2,
                    value=row.col_2
                )
                qty_cell.font = default_font

                # E → Precio €/Ud
                price_cell = ws.cell(
                    row=current_row,
                    column=start_col + 3,
                    value=row.col_3
                )
                price_cell.font = default_font

                # F → Total (fórmula Excel)
                total_cell = ws.cell(
                    row=current_row,
                    column=start_col + 4,
                    value=f"={qty_cell.coordinate}*{price_cell.coordinate}"
                )
                total_cell.font = default_font

                current_row += 1

        # =========================
        # INFO (comentarios)
        # =========================
        elif row.type == "INFO":
            ws.merge_cells(
                start_row=current_row,
                start_column=start_col,
                end_row=current_row,
                end_column=start_col + 4
            )

            cell = ws.cell(
                row=current_row,
                column=start_col,
                value=row.col_0
            )
            cell.font = default_font

            current_row += 1

        # =========================
        # EMPTY
        # =========================
        elif row.type == "EMPTY":
            current_row += 1

    wb.save(output_path)

    # ─────────────────────────────
    # Abrir automáticamente
    # ─────────────────────────────
    try:
        if platform.system() == "Windows":
            os.startfile(output_path)
        elif platform.system() == "Darwin":
            subprocess.call(["open", output_path])
        else:
            subprocess.call(["xdg-open", output_path])
    except Exception as e:
        print(f"No se pudo abrir automáticamente el archivo: {e}")

    return output_path
