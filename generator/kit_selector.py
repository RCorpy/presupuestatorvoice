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

AVAILABLE_KITS = [24, 18, 12, 6]


def select_kits(total_kg: float) -> Dict[int, int]:
    """
    Devuelve un dict {kit_size: amount} para cubrir total_kg.
    Ajusta total_kg al múltiplo de 6 más cercano hacia arriba.
    """
    if total_kg <= 0:
        return {}

    # 🔹 Redondear al múltiplo de 6 superior
    rounded_total = int(((total_kg + 5) // 6) * 6)

    # 🔹 Caso exacto predefinido
    if rounded_total in KIT_COMBINATIONS:
        return {
            size: qty
            for size, qty in KIT_COMBINATIONS[rounded_total].items()
            if qty > 0
        }

    # 🔹 Caso estándar: > 60 kg
    result: Dict[int, int] = {}
    remaining = rounded_total

    for kit in AVAILABLE_KITS:
        num_kits = remaining // kit
        if num_kits > 0:
            result[kit] = num_kits
            remaining -= kit * num_kits

    # 🔹 Si queda un resto, ponerlo en el kit más pequeño
    if remaining > 0:
        smallest_kit = min(AVAILABLE_KITS)
        result[smallest_kit] = result.get(smallest_kit, 0) + 1

    return result


