import warnings
import numpy as np
import xarray as xr


def cross_sec(data: xr.DataArray, x0, y0, x1, y1, num_points="auto"):
    """
    Converts 3D data to 2D data along the section (x0, y0) -> (x1, y1)

    Input:
        data: the data to interpolate
        (x0, y0): the starting point of the cross-section
        (x1, y1): the ending point of the cross-section
        num_points: how many points to return along the new axis

    Output:
        data_cs: the interpolated cross-section, with new dimension horz_dim

    Possible problems:
    - different names for lat/lon axes (perhaps add an optional argument for dim names?)
    - if num_points is not 'auto', then the resolution of the dataset changes, causing problems
      when doing further stuff like vertical interpolation

    Other stuff to possibly implement:
    - convert horz_dim to more useful units like distance/lat/lon (depends on shape)
    """

    if x0 == x1 and y0 == y1:
        raise ValueError("Start and end points are the same!")

    # simple cases: where the section is only along a single dimension
    # in this case, no interpolation is needed, just return the slice instead
    # renaming the sliced axis to horz_dim for consistency
    if x0 == x1:
        data_cs = data.sel(latitude=slice(y0, y1))
        data_cs = data_cs.sel(longitude=x0, method="nearest")
        data_cs = data_cs.rename({"latitude": "horz_dim"})
        return data_cs
    elif y0 == y1:
        data_cs = data.sel(longitude=slice(x0, x1))
        data_cs = data_cs.sel(latitude=y0, method="nearest")
        data_cs = data_cs.rename({"longitude": "horz_dim"})
        return data_cs

    x_min = min(data.longitude.values)
    x_max = max(data.longitude.values)

    y_min = min(data.latitude.values)
    y_max = max(data.latitude.values)

    # warn if one of the end points is out of range
    if (
        min(x0, x1) < x_min
        or max(x0, x1) > x_max
        or min(y0, y1) < y_min
        or max(y0, y1) > y_max
    ):
        warnings.warn(
            "End points are located outside the domain of the data. \
                        Setting end points to be on the boundary instead."
        )

    # cut off the relevant box
    data = data.sel(longitude=slice(min(x0, x1), max(x0, x1)))
    data = data.sel(latitude=slice(min(y0, y1), max(y0, y1)))
    # now update x0, x1, y0, y1 to the min/max values of the *sliced* data
    # this is important because if the input x0, etc. does not lie exactly on the data coordinates,
    # the resolution will be slightly changed, potentially causing problems down the line
    x0, x1 = min(data.longitude.values), max(data.longitude.values)
    y0, y1 = min(data.latitude.values), max(data.latitude.values)

    # now make a list of points to interpolate to

    x_num = data.longitude.size
    y_num = data.latitude.size
    if num_points == "auto":
        # by default, the resolution of the cross-section will be given by the longer axis
        num_points = max(x_num, y_num)

    if num_points == "auto":
        if x_num > y_num:
            x = data.longitude.values
            y = np.linspace(y0, y1, num_points)
        else:
            y = data.latitude.values
            x = np.linspace(x0, x1, num_points)
    else:
        x = np.linspace(x0, x1, num_points)  # data.longitude.values
        y = np.linspace(y0, y1, num_points)

    # convert x/y to DataArrays for xarray advanced interpolation
    x = xr.DataArray(x, dims="horz_dim")
    y = xr.DataArray(y, dims="horz_dim")

    # Let xarray handle the actual interpolation
    # (by default, this is linear interpolation)
    data_cs = data.interp(longitude=x, latitude=y)

    return data_cs
