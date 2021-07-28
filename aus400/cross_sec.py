import warnings
import numpy as np
import xarray as xr

def deg_to_dist(lons, lats):
    # function which takes [lon, lat] and returns [dist]
    # used to create nex axis for cross-sections
    
    Re = 6371e3 # radius of earth

    # convert to radians
    lons_rad = lons * np.pi/180
    lats_rad = lats * np.pi/180

    dlon = abs(lons_rad[1] - lons_rad[0])
    dlat = abs(lats_rad[1] - lats_rad[0])
    
    dx = Re * np.cos(lats_rad) * dlon
    dy = Re * dlat

    # length of diagonal
    ds = (dx**2 + dy**2) **0.5

    dist = np.cumsum(ds) / 1000 # in km

    return dist

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
                 (also contains distance as a coordinate along the cross-section)

    Possible problems:
    - if num_points is not 'auto', then the resolution of the dataset changes, causing problems
      when doing further stuff like vertical interpolation
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
    if x1 > x0:
        x0, x1 = min(data.longitude.values), max(data.longitude.values)
    else:
        x0, x1 = max(data.longitude.values), min(data.longitude.values)
    if y1 > y0:
        y0, y1 = min(data.latitude.values), max(data.latitude.values)
    else:
        y0, y1 = max(data.latitude.values), min(data.latitude.values)

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
        x = np.linspace(x0, x1, num_points)
        y = np.linspace(y0, y1, num_points)
    
    # convert x/y to DataArrays for xarray advanced interpolation
    x = xr.DataArray(x, dims="horz_dim")#, coords={"distance": horz_coords})
    y = xr.DataArray(y, dims="horz_dim")#, coords={"distance": horz_coords})

    # Let xarray handle the actual interpolation
    # (by default, this is linear interpolation)
    data_cs = data.interp(longitude=x, latitude=y)
    
    # calculate distance along horizontal to use as coords for new axis
    horz_coords = deg_to_dist(x.values, y.values)
    data_cs = data_cs.assign_coords(distance=("horz_dim", horz_coords))

    return data_cs
