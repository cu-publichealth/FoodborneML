from foodbornenyc.util.util import xuni

def test_xuni_blank():
    assert xuni(None) == u''
    assert xuni('') == u''
