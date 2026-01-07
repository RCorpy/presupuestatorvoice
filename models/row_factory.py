from .proforma_row import ProformaRow

def title_row(text: str) -> ProformaRow:
    return ProformaRow(
        type="TITLE",
        col_0=text
    )

def product_row(kit_text: str, product: str, uds, price, total) -> ProformaRow:
    return ProformaRow(
        type="PRODUCT",
        col_0=kit_text,
        col_1=product,
        col_2=str(uds),
        col_3=str(price),
        col_4=str(total),
    )

def info_row(left: str, right: str = "") -> ProformaRow:
    return ProformaRow(
        type="INFO",
        col_0=left,
        col_1=right,
    )

def empty_row() -> ProformaRow:
    return ProformaRow(type="EMPTY")
