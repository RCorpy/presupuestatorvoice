# commands/normalizer.py
def normalize_command(text: str) -> str:
    aliases = {
        "SI LA": "FILA",
        "SILA": "FILA"
    }
    for wrong, correct in aliases.items():
        text = text.replace(wrong, correct)
    return text
