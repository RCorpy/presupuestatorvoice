# generator/resin_color_capabilities.py

from generator.resin_config import (
    RESIN_SYSTEMS,
    COLORS,
    COLOR_IGNORED_PRODUCTS,
    ENABLE_DB_COLOR_FILTER,
)

def get_available_colors(system_key: str, materials_db: dict) -> list[str]:
    """
    Devuelve la lista de colores permitidos para una resina.
    """

    # 1️⃣ Resinas que ignoran color → solo BLANCO
    if system_key in COLOR_IGNORED_PRODUCTS:
        return ["BLANCO"]

    # 2️⃣ Si el filtro por DB está desactivado → todos los colores
    if not ENABLE_DB_COLOR_FILTER:
        return COLORS.copy()

    # 3️⃣ Filtro real contra la DB
    system = RESIN_SYSTEMS.get(system_key)
    if not system:
        return []

    base_name = system["product_base"]
    valid_colors = []

    for color in COLORS:
        product_name = f"{base_name} {color}"
        if product_name in materials_db:
            valid_colors.append(color)

    return valid_colors
