from ..cat import load
from ..cross_sec import cross_sec

def test_cross_sec():

    print('loading test dataset')
    ds = load(resolution="d0198", stream="spec", variable="sfc_temp", ensemble=0, time="20170328T1200")
    print('done')

    # lat slice
    x0, y0, x1, y1 = 130, -20, 135, -20
    ds_cs = cross_sec(ds, x0, y0, x1, y1)
    assert 'horz_dim' in ds_cs.dims

    # lon slice
    x0, y0, x1, y1 = 130, -20, 130, -25
    ds_cs = cross_sec(ds, x0, y0, x1, y1)
    assert 'horz_dim' in ds_cs.dims

    # diagonal slice
    x0, y0, x1, y1 = 130, -20, 135, -25
    ds_cs = cross_sec(ds, x0, y0, x1, y1)
    assert 'horz_dim' in ds_cs.dims

    # change no. of points
    ds_cs = cross_sec(ds, x0, y0, x1, y1, num_points=100)
    assert 'horz_dim' in ds_cs.dims
    assert ds_cs.horz_dim.size == 100


if __name__ == '__main__':
    test_cross_sec()
    print('passed all tests')
