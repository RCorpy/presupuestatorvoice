# generator/proforma_generator.py

from models.proforma_row import ProformaRow
from generator.resin_config import (
    IMPRIMACIONES,
    PRODUCT_INFO_RULES,
    STANDARD_USAGE_KG_PER_M2,
    TOOLS,
    DEFAULT_PRIMER_PRODUCT
)
from generator.kit_selector import select_kits


def generate_proforma(
    table_window,
    proforma_state,
    resin_type: str,
    work_type: str,
    area_m2: int,
    multiplier: float = 1.0,
    color: str = None,
    customer_name: str = None,
    customer_phone: str = None,
):
    """
    Genera o amplía una proforma en función del estado recibido.
    El reseteo del estado se controla desde la UI (MainWindow).
    """

    model = table_window.model
    table = table_window.table

    # -------------------------------------------------
    # 1️⃣ LIMPIEZA TOTAL DE UI + MODELO
    # (el estado YA viene limpio o acumulado)
    # -------------------------------------------------
    model.rows.clear()
    table.clearContents()
    table.setRowCount(0)
    table_window.active_row = 0

    table_window.sync_table_rows()
    table_window.refresh_all_rows()

    # -------------------------------------------------
    # 2️⃣ Datos de cliente (se sobrescriben siempre)
    # -------------------------------------------------
    proforma_state.set_customer(customer_name, customer_phone)

    # -------------------------------------------------
    # 3️⃣ IMPRIMACIÓN
    # -------------------------------------------------
    if "IMPRIMACIÓN" in work_type:
        primer_product = IMPRIMACIONES.get(resin_type, DEFAULT_PRIMER_PRODUCT)
        kg_total = area_m2 * STANDARD_USAGE_KG_PER_M2["IMPRIMACIÓN"]

        proforma_state.add_product_to_phase(
            phase_type="IMPRIMACIÓN",
            title="IMPRIMACIÓN",
            product_name=primer_product,
            kg=kg_total
        )

    # -------------------------------------------------
    # 4️⃣ CAPAS
    # -------------------------------------------------
    if "CAPA" in work_type:
        import re

        match = re.search(r"(\d+)", work_type)
        num_layers = int(match.group(1)) if match else 1

        title = f"{num_layers} CAPA{'S' if num_layers > 1 else ''}"
        if color:
            title += f" {color}"

        product_name = f"Kit {resin_type} {title}"
        kg_total = area_m2 * STANDARD_USAGE_KG_PER_M2["CAPA"] * num_layers

        proforma_state.add_product_to_phase(
            phase_type="CAPAS",
            title=title,
            product_name=product_name,
            kg=kg_total
        )

    # -------------------------------------------------
    # 5️⃣ RENDERIZAR TODA LA PROFORMA DESDE EL ESTADO
    # -------------------------------------------------
    rows = []

    # Cliente
    if proforma_state.customer_name or proforma_state.customer_phone:
        text = f"{proforma_state.customer_name or ''} {proforma_state.customer_phone or ''}".strip()
        rows.append(
            ProformaRow(
                type="TITLE",
                col_0="Cliente",
                col_1=text
            )
        )

    # Fases (IMPRIMACIÓN, CAPAS, etc.)
    for phase in proforma_state.phases:
        rows.append(
            ProformaRow(
                type="TITLE",
                col_0=phase.title
            )
        )

        for product_name, total_kg in phase.products.items():
            kit_distribution = select_kits(total_kg)

            for kit_size, amount in kit_distribution.items():
                if amount <= 0:
                    continue

                unit_price = round(100 * multiplier, 2)  # placeholder
                total_price = round(amount * unit_price, 2)

                rows.append(
                    ProformaRow(
                        type="PRODUCT",
                        col_0=f"{kit_size} kg",
                        col_1=product_name,
                        col_2=str(amount),
                        col_3=str(unit_price),
                        col_4=str(total_price)
                    )
                )

            info = PRODUCT_INFO_RULES.get(resin_type)
            if info:
                rows.append(
                    ProformaRow(
                        type="INFO",
                        col_0=info
                    )
                )

        rows.append(ProformaRow(type="EMPTY"))

    # -------------------------------------------------
    # 6️⃣ HERRAMIENTAS (una sola vez)
    # -------------------------------------------------
    if proforma_state.include_tools:
        rows.append(
            ProformaRow(
                type="TITLE",
                col_0="HERRAMIENTAS"
            )
        )

        for tool_name, amount, price in TOOLS:
            rows.append(
                ProformaRow(
                    type="PRODUCT",
                    col_0="",
                    col_1=tool_name,
                    col_2=str(amount),
                    col_3=str(price),
                    col_4=str(amount * price)
                )
            )

    # -------------------------------------------------
    # 7️⃣ INYECTAR FILAS EN EL MODELO
    # -------------------------------------------------
    for row in rows:
        model.add_row(row)

    table_window.sync_table_rows()
    table_window.refresh_all_rows()
    table_window.highlight_active_row()

    return rows
