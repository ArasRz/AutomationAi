def beräkna_rabatt(pris: float, rabattsats: float) -> float:
    return pris - (pris * rabattsats)


def test_normalt_fall():
    assert beräkna_rabatt(100, 0.1) == 90.0

def test_noll_rabatt():
    assert beräkna_rabatt(100, 0) == 100.0

def test_maximal_rabatt():
    assert beräkna_rabatt(100, 1) == 0.0

def test_negativt_pris():
    assert beräkna_rabatt(-100, 0.1) == -90.0
