from models.proforma_row import ProformaRow
from generator.resin_config import (
    IMPRIMACIONES,
    PRODUCT_INFO_RULES,
    STANDARD_USAGE_KG_PER_M2,
    TOOLS,
    DEFAULT_PRIMER_PRODUCT
)
from generator.kit_selector import select_kits
import re


def generate_proforma(
    table_window,
    resin_type: str,
    work_type: str,
    area_m2: int,
    multiplier: float = 1.0,
    color: str | None = None,
    customer_name: str | None = None,
    customer_phone: str | None = None
):
    """
    Genera la proforma completa en table_window.model.
    work_type: "IMPRIMACIÓN", "1 CAPA", "2 CAPAS",
               "IMPRIMACIÓN + 1 CAPA", etc.
    """
    model = table_window.model

    # -------------------------------------------------
    # 1️⃣ Limpiar completamente el modelo
    # -------------------------------------------------

    # LIMPIEZA TOTAL Y SEGURA
    model.rows.clear()
    table = table_window.table
    table.clearContents()
    table.setRowCount(0)
    table_window.active_row = 0

    table_window.sync_table_rows()
    table_window.refresh_all_rows()


    rows: list[ProformaRow] = []

    # -------------------------------------------------
    # 2️⃣ Cabecera cliente (opcional)
    # -------------------------------------------------
    if customer_name or customer_phone:
        info_text = f"{customer_name or ''} {customer_phone or ''}".strip()
        rows.append(
            ProformaRow(type="TITLE", col_0="CLIENTE", col_1=info_text)
        )

    # -------------------------------------------------
    # 3️⃣ IMPRIMACIÓN
    # -------------------------------------------------
    if "IMPRIMACIÓN" in work_type:
        rows.append(ProformaRow(type="TITLE", col_0="IMPRIMACIÓN"))

        product_name = IMPRIMACIONES.get(resin_type, DEFAULT_PRIMER_PRODUCT)
        total_kg = area_m2 * STANDARD_USAGE_KG_PER_M2["IMPRIMACIÓN"]
        kit_quantities = select_kits(total_kg)

        for kit_size, amount in kit_quantities.items():
            if amount <= 0:
                continue

            rows.append(ProformaRow(
                type="PRODUCT",
                col_0=f"{amount} kits {kit_size}kg",
                col_1=product_name,
                col_2=str(amount),
                col_3=str(round(100 * multiplier, 2)),
                col_4=str(round(amount * 100 * multiplier, 2))
            ))

            info_text = PRODUCT_INFO_RULES.get(resin_type)
            if info_text:
                rows.append(ProformaRow(type="INFO", col_0=info_text))

        rows.append(ProformaRow(type="EMPTY"))

    # -------------------------------------------------
    # 4️⃣ CAPAS (unificadas)
    # -------------------------------------------------
    if "CAPA" in work_type:
        match = re.search(r"(\d+)", work_type)
        num_layers = int(match.group(1)) if match else 1

        title = f"{num_layers} CAPA{'S' if num_layers > 1 else ''}"
        if color:
            title += f" · {color}"

        rows.append(ProformaRow(type="TITLE", col_0=title))

        total_kg = (
            area_m2
            * STANDARD_USAGE_KG_PER_M2["CAPA"]
            * num_layers
        )

        product_name = f"Kit {resin_type}"
        kit_quantities = select_kits(total_kg)

        for kit_size, amount in kit_quantities.items():
            if amount <= 0:
                continue

            rows.append(ProformaRow(
                type="PRODUCT",
                col_0=f"{amount} kits {kit_size}kg",
                col_1=product_name,
                col_2=str(amount),
                col_3=str(round(100 * multiplier, 2)),
                col_4=str(round(amount * 100 * multiplier, 2))
            ))

            info_text = PRODUCT_INFO_RULES.get(resin_type)
            if info_text:
                rows.append(ProformaRow(type="INFO", col_0=info_text))

        rows.append(ProformaRow(type="EMPTY"))

    # -------------------------------------------------
    # 5️⃣ HERRAMIENTAS (siempre al final)
    # -------------------------------------------------
    rows.append(ProformaRow(type="TITLE", col_0="HERRAMIENTAS"))

    for tool_name, amount, price in TOOLS:
        rows.append(ProformaRow(
            type="PRODUCT",
            col_0="",
            col_1=tool_name,
            col_2=str(amount),
            col_3=str(price),
            col_4=str(amount * price)
        ))

    # -------------------------------------------------
    # 6️⃣ Volcar filas al modelo
    # -------------------------------------------------
    for row in rows:
        model.add_row(row)

    # -------------------------------------------------
    # 7️⃣ Refresco FINAL seguro
    # -------------------------------------------------
    table_window.active_row = 0
    table_window.sync_table_rows()
    table_window.refresh_all_rows()
    table_window.highlight_active_row()

    return rows
