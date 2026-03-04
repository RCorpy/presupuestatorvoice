from models.proforma_model import ProformaModel
from models.proforma_row import ProformaRow


def test_packaging_cost_respects_base():
    model = ProformaModel()
    # assign dummy prices
    model.materials['ACRILICA'] = {'price': 100}
    model.materials['EPOXI_AM'] = {'price': 100}

    # acrilica uses base 5, kit 10 kg -> packaging = 10 * PACKAGING_COST_PER_PHASE / 5
    row = ProformaRow(type="PRODUCT", col_0="10 kg", col_1="ACRILICA", col_2="1")
    model.rows = [row]
    model.set_product(0, "ACRILICA", 1.0)
    unit_price_acri = float(model.rows[0].col_3)
    assert unit_price_acri > 1000  # some packaging cost added

    # epoxy uses base 6, kit 6 kg -> packaging = 6 * PACKAGING_COST_PER_PHASE / 6
    row2 = ProformaRow(type="PRODUCT", col_0="6 kg", col_1="EPOXI_AM", col_2="1")
    model.rows = [row2]
    model.set_product(0, "EPOXI_AM", 1.0)
    unit_price_epo = float(model.rows[0].col_3)
    assert unit_price_epo > 600

    print("proforma_model tests passed")


if __name__ == "__main__":
    test_packaging_cost_respects_base()
