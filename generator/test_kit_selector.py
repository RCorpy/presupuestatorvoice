from generator.kit_selector import select_kits


def test_select_kits_base6_exact():
    # values that match the precomputed combinations
    assert select_kits(6) == {6: 1}
    assert select_kits(30) == {18: 1, 12: 1}
    assert select_kits(60) == {24: 2, 12: 1}


def test_select_kits_base6_rounding():
    # fractional totals should round up to nearest 6
    dist = select_kits(7)
    total = sum(k * v for k, v in dist.items())
    assert total % 6 == 0
    assert total >= 7


def test_select_kits_base5_rounds():
    # for base5, the returned distribution should cover at least the
    # rounded-up multiple of 5 (the algorithm always rounds up to base).
    dist = select_kits(7, base=5)
    total = sum(k * v for k, v in dist.items())
    rounded = ((7 + 5 - 1) // 5) * 5
    assert total >= rounded



def test_select_kits_base5_distribution():
    # ensure kits are chosen greedily when base=5
    dist = select_kits(26, base=5)
    total = sum(k * v for k, v in dist.items())
    assert total >= 26
    # for base5 kits we expect the largest unit (25) to be used when possible
    assert 25 in dist


if __name__ == "__main__":
    test_select_kits_base6_exact()
    test_select_kits_base6_rounding()
    test_select_kits_base5_rounds()
    test_select_kits_base5_distribution()
    print("kit_selector tests passed")
