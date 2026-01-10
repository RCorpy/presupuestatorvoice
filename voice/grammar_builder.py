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
    print(materials)
    for name in materials.keys():
        grammar.add(name.lower())
    print("printing grammar")
    
    return sorted(grammar)