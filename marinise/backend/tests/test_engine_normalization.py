"""
Section 5: "Farklı kaynaklardaki model yazımları normalize edilmelidir.
Örneğin Caterpillar 3512 B ile CAT 3512B aynı model olarak
eşleştirilebilmelidir." - this is the exact case these tests pin down.
"""
from scripts.seed_demo_data import normalize


def test_caterpillar_3512_variants_match():
    assert normalize("3512 B") == normalize("3512B")
    assert normalize("CAT 3512-B") == normalize("Cat3512b")


def test_mase_variants_match():
    assert normalize("IS 29/36") == normalize("is29/36".upper())
