import warnings
import numpy as np
import xarray as xr

def deg_to_dist(lons, lats):
    """
    Converts an array of latitudes and longitudes to distance from 1st point
    Used as a coordinate for cross-sections

    Input:
        lons: array of longitude points
        lats: array of latitude points
        (lats and lons must be the same size)
    Output:
        dist: array of cumulative distances from the first point
    """
    
    Re = 6371e3 # radius of earth

    # convert to radians
    lons_rad = lons * np.pi/180
    lats_rad = lats * np.pi/180
    
    # 3 cases:
    # 1. meridional segment
    if lons_rad.size == 1:
        dlat = abs(lats_rad[1] - lats_rad[0])
        ds = Re * dlat
        ds = np.repeat(ds, lats_rad.size) # vectorise
    
    # 2. zonal segment
    elif lats_rad.size == 1:
        dlon = abs(lons_rad[1] - lons_rad[0])
        ds = Re * np.cos(lats_rad) * dlon
        ds = np.repeat(ds, lons_rad.size) # vectorise
    
    # 3. diagonal segment
    else:
        dlon = abs(lons_rad[1] - lons_rad[0])
        dlat = abs(lats_rad[1] - lats_rad[0])
        
        dx = Re * np.cos(lats_rad) * dlon
        dy = Re * dlat

        # length of diagonal (should already be a vector)
        ds = (dx**2 + dy**2) ** 0.5        

    dist = np.cumsum(ds) / 1000 # in km

    return dist

def cross_sec(data: xr.DataArray, x0, y0, x1, y1, num_points="auto"):

    if x0 == x1 and y0 == y1:
        raise ValueError("Start and end points are the same!")

    # simple cases: where the section is only along a single dimension
    # in this case, no interpolation is needed, just return the slice instead
    # renaming the sliced axis to horz_dim for consistency
    if x0 == x1:

        data_cs = data.sel(latitude=slice(min(y0, y1), max(y0, y1)))
        data_cs = data_cs.sel(longitude=x0, method="nearest")
        
        # calculate distance and label it as the new dimension
        distance = deg_to_dist(data_cs.longitude.values, data_cs.latitude.values)
        data_cs = data_cs.assign_coords(distance=('latitude', distance))
        data_cs = data_cs.swap_dims({'latitude': 'distance'})
        
        return data_cs
    
    elif y0 == y1:

        data_cs = data.sel(longitude=slice(min(x0, x1), max(x0, x1)))
        data_cs = data_cs.sel(latitude=y0, method="nearest")
        
        # calculate distance and label it as the new dimension
        distance = deg_to_dist(data_cs.longitude.values, data_cs.latitude.values)
        data_cs = data_cs.assign_coords(distance=('longitude', distance))
        data_cs = data_cs.swap_dims({'longitude': 'distance'})
        
        return data_cs
    
    # standard case (diagonal cross-section)
    else:

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
    
    # calculate distance along horizontal to use as coords for new axis
    distance = deg_to_dist(x, y)
    
    # convert x/y to DataArrays for xarray advanced interpolation
    x = xr.DataArray(x, dims="distance", coords={"distance": distance})
    y = xr.DataArray(y, dims="distance", coords={"distance": distance})

    # Let xarray handle the actual interpolation
    # (by default, this is linear interpolation)
    data_cs = data.interp(longitude=x, latitude=y)

    return data_cs