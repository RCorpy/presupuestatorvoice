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

ENABLE_DB_COLOR_FILTER = False

#COSTES DE ENVASE

PACKAGING_COST_PER_PHASE = 6.5
BOX_COST = 3.0
BUCKET_COST = 3.5
#FIN COSTES DE ENVASE

RESIN_SYSTEMS = {
    "EPOXI_AM": {
        "label": "Epoxi AM",
        "product_base": "KIT EPOXI AM",
        "primer": "KIT IMPRIMACION EPOXI",
        "usage_kg_per_m2": {
            "IMPRIMACION": 0.15,
            "CAPA": 0.15,
        },
        "cost_multiplier": 3.0,
        "product_info": "Catalizador 5:1",
    },

    "EPOXI_AMX": {
        "label": "Epoxi AMX",
        "product_base": "KIT EPOXI AMX",
        "primer": "KIT IMPRIMACION EPOXI",
        "usage_kg_per_m2": {
            "IMPRIMACION": 0.15,
            "CAPA": 0.15,
        },
        "cost_multiplier": 2.9,
        "product_info": "Catalizador 5:1",
    },

    "EPOXI_ITV": {
        "label": "Epoxi ITV",
        "product_base": "KIT EPOXI ITV",
        "primer": "KIT IMPRIMACION EPOXI",
        "usage_kg_per_m2": {
            "IMPRIMACION": 0.15,
            "CAPA": 0.15,
        },
        "cost_multiplier": 3.1,
        "product_info": "Sistema reforzado ITV",
    },

    "POLITOP": {
        "label": "Politop",
        "product_base": "POLITOP",
        "primer": None,
        "usage_kg_per_m2": {
            "IMPRIMACION": 0.15,
            "CAPA": 0.15,
        },
        "cost_multiplier": 3.0,
        "product_info": "Resina monocomponente",
    },

    "LSB": {
        "label": "Resina LSB",
        "product_base": "KIT LSB",
        "primer": None,
        "usage_kg_per_m2": {
            "IMPRIMACION": 1.0,
            "CAPA": 1.0,
        },
        "cost_multiplier": 2.2,
        "product_info": "Sistema autonivelante",
    },

    "ACRILICA": {
        "label": "Acrilica",
        "product_base": "ACRILICA",
        "primer": None,
        "usage_kg_per_m2": {
            "IMPRIMACION": 0.15,
            "CAPA": 0.15,
        },
        "cost_multiplier": 2.95,
        "product_info": "Secado rápido",
    },

    "EPOXI_MATE": {
        "label": "Epoxi Mate",
        "product_base": "KIT EPOXI MATE",
        "primer": "KIT IMPRIMACION EPOXI",
        "usage_kg_per_m2": {
            "IMPRIMACION": 0.15,
            "CAPA": 0.15,
        },
        "cost_multiplier": 2.5,
        "product_info": "Catalizador 10:1",
    },

    "TOP_COAT_2023": {
        "label": "Top Coat 2023",
        "product_base": "KIT TOP COAT 2023",
        "primer": None,
        "usage_kg_per_m2": {
            "IMPRIMACION": 0.10,
            "CAPA": 0.10,
        },
        "cost_multiplier": 2.5,
        "product_info": "Catalizador 2:1",
    },

    "TOP_COAT_2025": {
        "label": "Top Coat 2025",
        "product_base": "KIT TOP COAT 2025",
        "primer": None,
        "usage_kg_per_m2": {
            "IMPRIMACION": 0.10,
            "CAPA": 0.10,
        },
        "cost_multiplier": 2.5,
        "product_info": "Catalizador 5:1?",
    },

    "EPOXI_NORMA_ISO": {
        "label": "Epoxi Antibacteriano",
        "product_base": "KIT EPOXI ATB",
        "primer": "KIT IMPRIMACION EPOXI",
        "usage_kg_per_m2": {
            "IMPRIMACION": 0.15,
            "CAPA": 0.15,
        },
        "cost_multiplier": 3.0,
        "product_info": "Antibacteriano",
    },

    "RIVER_TABLE_3": {
        "label": "River Table 03",
        "product_base": "KIT RIVER TABLE",
        "primer": None,
        "usage_kg_per_m2": {
            "IMPRIMACION": 1.0,
            "CAPA": 1.0,
        },
        "cost_multiplier": 2.2,
        "product_info": "Resina Mesas 1-3 cm",
    },

    "RIVER_TABLE_5": {
        "label": "River Table 05",
        "product_base": "KIT RIVER TABLE",
        "primer": None,
        "usage_kg_per_m2": {
            "IMPRIMACION": 1.0,
            "CAPA": 1.0,
        },
        "cost_multiplier": 2.2,
        "product_info": "Resina Mesas 3-5 cms",
    },

    "EPOXI_MASILLA": {
        "label": "Masilla",
        "product_base": "KIT IMPRIMACION EPOXI",
        "primer": None,
        "usage_kg_per_m2": {
            "IMPRIMACION": 1.0,
            "CAPA": 1.0,
        },
        "cost_multiplier": 3.0,
        "product_info": "Primer",
    },

    "PRIMER_HUMEDAD": {
        "label": "Primer Humedad",
        "product_base": "KIT IMPRIMACION EPOXI HUMEDAD",
        "primer": None,
        "usage_kg_per_m2": {
            "IMPRIMACION": 0.15,
            "CAPA": 0.15,
        },
        "cost_multiplier": 3.0,
        "product_info": "Top Coat 2025",
    },

    "PRIMER_COLOR": {
        "label": "Primer Color",
        "product_base": "KIT IMPRIMACION COLOR",
        "primer": None,
        "usage_kg_per_m2": {
            "IMPRIMACION": 0.15,
            "CAPA": 0.15,
        },
        "cost_multiplier": 3.0,
        "product_info": "Catalizador 5:1",
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
    "ROJO FERRARI",
    "NARANJA",
    "OCRE",
    "GRIS ANTRACITA",
    "AZUL 5015",
    "AZUL 5002",
    "AZUL 5012",
]

COLOR_IGNORED_PRODUCTS = {
    "LSB": "KIT LSB",
    "TOP_COAT_2023": "KIT TOP COAT 2023",
    "TOP_COAT_2025": "KIT TOP COAT 2025",
    "RIVER_TABLE_3": "KIT RIVER TABLE",
    "RIVER_TABLE_5": "KIT RIVER TABLE",
    "EPOXI_MASILLA": "KIT IMPRIMACION EPOXI",
    "PRIMER_HUMEDAD": "KIT IMPRIMACION EPOXI HUMEDAD",
}


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


def build_product_name(system_key: str, color: str | None) -> str:
    system = RESIN_SYSTEMS[system_key]

    # 1️⃣ Productos que ignoran color
    if system_key in COLOR_IGNORED_PRODUCTS:
        return COLOR_IGNORED_PRODUCTS[system_key]

    base = system["product_base"]

    # 2️⃣ Si no hay color, devolver base
    if not color:
        return base

    # 3️⃣ Caso normal: producto + color
    return f"{base} {color}"

