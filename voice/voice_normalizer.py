# commands/normalizer.py

def normalize_command(text: str) -> str:
    text = text.upper()

    # --------------------------------------------------
    # Correcciones directas de frases completas
    # --------------------------------------------------
    phrase_aliases = {
        "SI LA": "FILA",
        "SILA": "FILA",
    }

    for wrong, correct in phrase_aliases.items():
        text = text.replace(wrong, correct)

    # --------------------------------------------------
    # Normalización de palabras sueltas (dominio)
    # --------------------------------------------------
    word_aliases = {
        # Fonética / reconocimiento
        "TOP": "POLITOP",
        "ACRILICA": "ENEKRIL",
        "ACRILICO": "ENEKRIL",

        # Variantes comunes
        "EPOXY": "EPOXI",
        "EPOSI": "EPOXI",
        "NO": "CANCELAR",
    }

    tokens = text.split()
    normalized_tokens = [
        word_aliases.get(token, token)
        for token in tokens
    ]

    return " ".join(normalized_tokens)
