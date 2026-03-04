# generator/kit_selector.py

from typing import Dict

# Combinaciones óptimas hasta 60 kg
# formato:
# total_kg: { kit_size: amount }
KIT_COMBINATIONS: Dict[int, Dict[int, int]] = {
    6:  {6: 1},
    12: {12: 1},
    18: {18: 1},
    24: {24: 1},
    30: {18: 1, 12: 1},
    36: {18: 2},
    42: {24: 1, 18: 1},
    48: {24: 2},
    54: {36: 0, 18: 3},  # equivalente a 3x18
    60: {24: 2, 12: 1},
}

# kits disponibles para cada múltiplo
AVAILABLE_KITS_BASE6 = [24, 18, 12, 6]  # sistema estándar (múltiplo de 6)
AVAILABLE_KITS_BASE5 = [25, 20, 15, 10, 5]  # kits típicos para productos de base 5


def select_kits(total_kg: float, base: int = 6) -> Dict[int, int]:
    """
    Devuelve un dict {kit_size: amount} para cubrir total_kg.
    Ajusta total_kg al múltiplo de `base` más cercano hacia arriba.
    La mayoría de productos usan base=6, pero algunos (p.ej. Acrilica/Politop)
    trabajan en múltiplos de 5 y pasarán base=5.
    """
    if total_kg <= 0:
        return {}

    # 🔹 Redondear al múltiplo de "base" superior
    rounded_total = int(((total_kg + base - 1) // base) * base)

    # 🔹 Caso exacto predefinido (solo tenemos combos optimizados para base6)
    if base == 6 and rounded_total in KIT_COMBINATIONS:
        return {
            size: qty
            for size, qty in KIT_COMBINATIONS[rounded_total].items()
            if qty > 0
        }

    # 🔹 Caso estándar: >= max de combos o base != 6
    result: Dict[int, int] = {}
    remaining = rounded_total

    # elegir lista de kits en función del múltiplo
    kit_list = AVAILABLE_KITS_BASE5 if base == 5 else AVAILABLE_KITS_BASE6

    for kit in kit_list:
        num_kits = remaining // kit
        if num_kits > 0:
            result[kit] = num_kits
            remaining -= kit * num_kits

    # 🔹 Si queda un resto, ponerlo en el kit más pequeño
    if remaining > 0:
        smallest_kit = min(kit_list)
        result[smallest_kit] = result.get(smallest_kit, 0) + 1

    return result


