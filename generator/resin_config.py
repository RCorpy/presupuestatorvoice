# generator/resin_config.py

# =========================================================
# Sistemas de resina disponibles
# =========================================================
# Cada sistema define:
# - nombre visible
# - nombre base del producto para DB
# - imprimaciOn asociada
# - consumo estándar por m² y capa
# - multiplicador de coste
# - información extra (fila INFO en UI)
# =========================================================

RESIN_SYSTEMS = {
    "EPOXI_AM": {
        "label": "Epoxi AM",
        "product_base": "KIT EPOXI AM",
        "primer": "KIT IMPRIMACION AM",
        "usage_kg_per_m2": {
            "IMPRIMACION": 0.20,
            "CAPA": 0.20,
        },
        "cost_multiplier": 3,
        "product_info": "Catalizador 5:1",
    },
    "EPOXI_AMX": {
        "label": "Epoxi AMX",
        "product_base": "KIT EPOXI AMX",
        "primer": "KIT IMPRIMACION AMX",
        "usage_kg_per_m2": {
            "IMPRIMACION": 0.20,
            "CAPA": 0.20,
        },
        "cost_multiplier": 2.9,
        "product_info": "Catalizador 5:1",
    },
    "EPOXI_ITV": {
        "label": "Epoxi ITV",
        "product_base": "KIT EPOXI ITV",
        "primer": "KIT IMPRIMACION ITV",
        "usage_kg_per_m2": {
            "IMPRIMACION": 0.20,
            "CAPA": 0.20,
        },
        "cost_multiplier": 3.1,
        "product_info": "Sistema reforzado ITV",
    },
    "POLITOP": {
        "label": "Politop",
        "product_base": "KIT POLITOP",
        "primer": "KIT POLITOP PRIMER",
        "usage_kg_per_m2": {
            "IMPRIMACION": 0.20,
            "CAPA": 0.20,
        },
        "cost_multiplier": 3,
        "product_info": "Resina monocomponente",
    },
    "LSB": {
        "label": "Resina LSB",
        "product_base": "KIT LSB",
        "primer": "KIT IMPRIMACION LSB",
        "usage_kg_per_m2": {
            "IMPRIMACION": 0.20,
            "CAPA": 0.30,
        },
        "cost_multiplier": 3.1,
        "product_info": "Sistema autonivelante",
    },
    "ACRILICA": {
        "label": "Acrilica",
        "product_base": "KIT ACRILICA",
        "primer": "KIT IMPRIMACION ACRILICA",
        "usage_kg_per_m2": {
            "IMPRIMACION": 0.15,
            "CAPA": 0.15,
        },
        "cost_multiplier": 2.95,
        "product_info": "Secado rápido",
    },
}

# =========================================================
# Colores disponibles
# =========================================================

COLORS = [
    "BLANCO",
    "NEGRO",
    "GRIS",
    "GRIS CLARO",
    "GRIS OSCURO",
    "VERDE",
    "ROJO",
    "AZUL",
    "AMARILLO",
    "BEIGE",
]

# =========================================================
# Kits disponibles por tamaño (kg)
# =========================================================

KITS_AVAILABLE = [6, 12, 18, 24]

# =========================================================
# Herramientas estándar
# =========================================================

TOOLS = [
    ("Báscula", 1, 0),
    ("Rodillos", 3, 0),
    ("Cubos de mezcla", 3, 0),
]

# =========================================================
# Valores por defecto / fallback
# =========================================================

DEFAULT_PRIMER_PRODUCT = "IMPRIMACION GENERICA"

# =========================================================
# Helpers (para usar desde el generador)
# =========================================================

def get_product_base(system_key: str) -> str:
    return RESIN_SYSTEMS[system_key]["product_base"]


def get_primer_product(system_key: str) -> str:
    return RESIN_SYSTEMS.get(system_key, {}).get(
        "primer", DEFAULT_PRIMER_PRODUCT
    )


def get_usage_kg_per_m2(system_key: str, phase: str) -> float:
    """
    phase: 'IMPRIMACION' o 'CAPA'
    """
    return RESIN_SYSTEMS[system_key]["usage_kg_per_m2"].get(phase, 0)


def get_cost_multiplier(system_key: str) -> float:
    return RESIN_SYSTEMS[system_key]["cost_multiplier"]


def get_product_info(system_key: str) -> str:
    return RESIN_SYSTEMS[system_key].get("product_info", "")


def build_product_name(system_key: str, color: str) -> str:
    """
    El nombre NO depende de las capas.
    Ejemplo:
    KIT EPOXI AM VERDE
    """
    base = get_product_base(system_key)
    return f"{base} {color}"
