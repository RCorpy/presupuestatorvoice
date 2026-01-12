#grammar_builder.py

BASE_GRAMMAR = [
    "fila",
    "cantidad",
    "precio",
    "siguiente",
    "cancelar",
    "producto",
    "nuevo",
    "nueva",
    "titulo",
    "detalle", 
    "vacia",
    "borrar",
    "coma",
    "punto",
    "acrilica",
    "no",
    "si",
    "polizon",
    "cero","uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez",
]

def build_grammar(materials: dict) -> list[str]:
    grammar = set(BASE_GRAMMAR)
    for name in materials.keys():
        grammar.add(name.lower())
    
    return sorted(grammar)