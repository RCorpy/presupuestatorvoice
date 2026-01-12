# generator/resin_config.py

# Imprimación estándar por resina
IMPRIMACIONES = {
    "EPOXI": "KIT EPOXI PRIMER",
    "POLITOP": "POLITOP BLANCO",
    "IMPRIMACIÓN": "IMPRIMACIÓN GENÉRICA"
}

# Kits disponibles por tamaño
KITS_AVAILABLE = [6, 12, 18, 24]  # en kg

# Información extra de productos según tipo de resina
PRODUCT_INFO_RULES = {
    "EPOXI": "Catalizador 5:1",
    "POLITOP": "Resina monocomponente",
    "IMPRIMACIÓN": "Catalizador 5:1"
}

# Cantidades estándar por m² en kg
STANDARD_USAGE_KG_PER_M2 = {
    "IMPRIMACIÓN": 0.2,  # 200 g/m²
    "CAPA": 0.2           # 200 g/m²
}

# Herramientas estándar
TOOLS = [
    ("Báscula", 1, 0),
    ("Rodillos", 3, 0),
    ("Cubos de mezcla", 3, 0)
]

# Producto estándar genérico en caso de no encontrar imprimación
DEFAULT_PRIMER_PRODUCT = "IMPRIMACIÓN GENÉRICA"
