# commands/product_resolver.py
import re


def normalize_tokens(text: str) -> list[str]:
    """
    Convierte un texto en tokens comparables:
    - mayúsculas
    - sin símbolos
    - separa números y letras
    """
    text = text.upper()
    text = re.sub(r"[^A-Z0-9 ]", " ", text)
    return text.split()


def resolve_products(buffer_tokens: list[str], products: list[str]) -> list[str]:
    buffer_tokens = merge_numeric_tokens(
        [t.upper() for t in buffer_tokens]
    )

    matches = []

    for product in products:
        product_tokens = normalize_tokens(product)

        if all(token in product_tokens for token in buffer_tokens):
            matches.append(product)

    return matches


def merge_numeric_tokens(tokens: list[str]) -> list[str]:
    """
    Une secuencias consecutivas de dígitos:
    ["7", "0", "4", "1"] → ["7041"]
    """
    merged = []
    buffer = ""

    for token in tokens:
        if token.isdigit():
            buffer += token
        else:
            if buffer:
                merged.append(buffer)
                buffer = ""
            merged.append(token)

    if buffer:
        merged.append(buffer)

    return merged
