# generator/proforma_generator.py

from models.proforma_row import ProformaRow
from generator.resin_config import (
    get_primer_product,
    get_usage_kg_per_m2,
    build_product_name,
    get_product_info,
    TOOLS,
)
from generator.kit_selector import select_kits


def generate_proforma(
    table_window,
    proforma_state,
    system_key: str,
    work_type: str,
    area_m2: int,
    multiplier: float = 3.0,
    color: str = None,
    customer_name: str = None,
    customer_phone: str = None,
):
    """
    Genera o amplía una proforma en función del estado recibido.
    El reseteo del estado se controla desde la UI.
    """

    model = table_window.model
    table = table_window.table

    # -------------------------------------------------
    # 1️⃣ LIMPIEZA DE UI + MODELO
    # -------------------------------------------------
    model.rows.clear()
    table.clearContents()
    table.setRowCount(0)
    table_window.active_row = 0

    table_window.sync_table_rows()
    table_window.refresh_all_rows()

    # -------------------------------------------------
    # 2️⃣ Datos de cliente
    # -------------------------------------------------
    proforma_state.set_customer(customer_name, customer_phone)

    # -------------------------------------------------
    # 3️⃣ IMPRIMACION
    # -------------------------------------------------
    if "IMPRIMACION" in work_type:
        primer_product = get_primer_product(system_key)
        kg_per_m2 = get_usage_kg_per_m2(system_key, "IMPRIMACION")
        kg_total = area_m2 * kg_per_m2

        proforma_state.add_product_to_phase(
            phase_type="IMPRIMACION",
            title="IMPRIMACION",
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

        product_name = build_product_name(system_key, color)
        kg_per_m2 = get_usage_kg_per_m2(system_key, "CAPA")
        kg_total = area_m2 * kg_per_m2 * num_layers

        proforma_state.add_product_to_phase(
            phase_type="CAPAS",
            title=title,
            product_name=product_name,
            kg=kg_total
        )

    # -------------------------------------------------
    # 5️⃣ RENDERIZADO DESDE EL ESTADO
    # -------------------------------------------------
    rows = []

    # Cliente
    if proforma_state.customer_name or proforma_state.customer_phone:
        text = f"{proforma_state.customer_name or ''} {proforma_state.customer_phone or ''}".strip()
        rows.append(ProformaRow(type="TITLE", col_0="Cliente", col_1=text))

    # Fases
    for phase in proforma_state.phases:
        rows.append(ProformaRow(type="TITLE", col_0=phase.title))

        for product_name, total_kg in phase.products.items():
            kit_distribution = select_kits(total_kg)

            for kit_size, amount in kit_distribution.items():
                if amount <= 0:
                    continue

                # Crear la fila
                row = ProformaRow(
                    type="PRODUCT",
                    col_0=f"{kit_size} kg",
                    col_1=product_name,
                    col_2=str(amount),
                    col_3="",  # temporal, será reemplazado
                    col_4="",  # temporal
                )

                # Rellenar el precio desde la BD usando el modelo
                price = table_window.model.get_price_from_db(product_name)
                if price is not None:
                    kit_multiplier = float(kit_size)
                    final_price = price * multiplier * kit_multiplier
                    row.col_3 = str(round(final_price, 2))
                    row.col_4 = str(round(amount * final_price, 2))
                else:
                    row.col_3 = "not found"
                    row.col_4 = ""


                # Añadir fila al modelo temporal
                rows.append(row)


            info = get_product_info(system_key)
            if info:
                rows.append(ProformaRow(type="INFO", col_0=info))

        rows.append(ProformaRow(type="EMPTY"))

    # -------------------------------------------------
    # 6️⃣ HERRAMIENTAS
    # -------------------------------------------------
    if proforma_state.include_tools:
        rows.append(ProformaRow(type="TITLE", col_0="HERRAMIENTAS"))

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
    # 7️⃣ INYECCIÓN EN EL MODELO
    # -------------------------------------------------
    for row in rows:
        model.add_row(row)

    table_window.sync_table_rows()
    table_window.refresh_all_rows()
    table_window.highlight_active_row()

    return rows
