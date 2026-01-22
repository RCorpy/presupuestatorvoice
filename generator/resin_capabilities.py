# generator/resin_capabilities.py

# =========================================================
# Capacidades de cada sistema de resina
# =========================================================
# PRIMER = permite imprimación
# CAPA   = permite capas
# =========================================================

RESIN_CAPABILITIES = {
    "EPOXI_AM": {"PRIMER", "CAPA"},
    "EPOXI_AMX": {"PRIMER", "CAPA"},
    "EPOXI_ITV": {"PRIMER", "CAPA"},
    "POLITOP": {"CAPA"},
    "LSB": {"CAPA"},
    "ACRILICA": {"CAPA"},
    "EPOXI_MATE": {"PRIMER", "CAPA"},
    "TOP_COAT_2023": {"CAPA"},
    "TOP_COAT_2025": {"CAPA"},
    "EPOXI_NORMA_ISO": {"PRIMER", "CAPA"},
    "RIVER_TABLE_3": {"CAPA"},
    "RIVER_TABLE_5": {"CAPA"},
    "EPOXI_MASILLA": {"CAPA"},
    "PRIMER_HUMEDAD": {"CAPA"},
    "PRIMER_COLOR": {"CAPA"},
}

# =========================================================
# Traducción capacidades → tipos de trabajo UI
# =========================================================

def get_valid_work_types(system_key: str, all_work_types: list[str]) -> list[str]:
    """
    Devuelve la lista de trabajos válidos para el sistema de resina dado.
    """
    capabilities = RESIN_CAPABILITIES.get(system_key, set())
    valid = []

    for work in all_work_types:
        has_primer = "IMPRIMACION" in work
        has_capa = "CAPA" in work

        # Casos inválidos
        if has_primer and "PRIMER" not in capabilities:
            continue
        if has_capa and "CAPA" not in capabilities:
            continue

        valid.append(work)

    return valid
