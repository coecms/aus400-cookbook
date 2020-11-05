from ..cat import *


def test_load():
    ds = load(
        resolution="d0036",
        stream="spec",
        variable="sfc_temp",
        ensemble=0,
        time="20170328T1200",
    )

    assert "sfc_temp" in ds


def test_filter():
    cat = filter_catalogue(
        resolution="d0036",
        stream="spec",
        variable="sfc_temp",
        time=slice("20170326T0000", "20170327T0000"),
    )

    assert len(cat) == 13

    cat = filter_catalogue(
        resolution="d0036",
        stream="spec",
        variable="sfc_temp",
        time="20170328T1200",
    )

    assert len(cat) == 1

    cat = filter_catalogue(
        resolution="d0036",
        stream="spec",
        variable="sfc_temp",
        time="20170328T1200",
        ensemble=slice(0, 0),
    )

    assert len(cat) == 1

    cat = filter_catalogue(
        resolution="d0036",
        stream="spec",
        variable="sfc_temp",
        time=slice("20170326T0000", "20170326T0000"),
    )

    assert len(cat) == 1
