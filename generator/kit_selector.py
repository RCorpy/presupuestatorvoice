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


def select_kits(total_kg: int) -> Dict[int, int]:
    """
    Devuelve un dict {kit_size: amount} para cubrir total_kg
    """

    if total_kg <= 0:
        return {}

    # Caso exacto predefinido
    if total_kg in KIT_COMBINATIONS:
        # limpiar posibles ceros
        return {
            size: qty
            for size, qty in KIT_COMBINATIONS[total_kg].items()
            if qty > 0
        }

    # Caso estándar: > 60 kg
    result: Dict[int, int] = {}

    remaining = total_kg

    # tantos kits de 24 como se pueda
    kits_24 = remaining // 24
    if kits_24 > 0:
        result[24] = kits_24
        remaining -= kits_24 * 24

    if remaining == 0:
        return result

    # resto en UN solo kit
    remainder_kit = _closest_single_kit(remaining)
    result[remainder_kit] = result.get(remainder_kit, 0) + 1

    return result


def _closest_single_kit(kg: int) -> int:
    """
    Devuelve el tamaño de kit más cercano >= kg
    """
    for size in AVAILABLE_KITS:
        if size >= kg:
            return size

    # si es mayor que 24 (caso raro, pero seguro)
    return 24
