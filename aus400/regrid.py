#!/usr/bin/env python
# Copyright 2020 Scott Wales
# author: Scott Wales <scott.wales@unimelb.edu.au>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Regridding operations for Aus400 data

Aus400 data is on two main resolutions, 'd0036' - a 0.0036 degree grid spacing
(equivalent to 400m at the equator) and 'd0198' - a 0.0198 degree grid spacing
(equivalent to 2.2 km at the equator).

The Unified Model used to run the Aus400 experiment uses an Arakawa C grid.
Scalar quantities are defined at grid centres, vector quantities on grid edges.
Scalar quantites are on the 't' grid, e.g. 'd0036t', and are offset half a grid
spacing E-W from 'd0036u' and N-S from 'd0036v'.

The default regridding uses bilinear interpolation. For custom regridding grid
definitions may be found in the 'grids/' directory of the Aus400 published
dataset, for use by e.g. ESMF_RegridWeightGen.
"""

import xarray
from climtas.regrid import regrid
from .cat import root, load_var
import numpy
import pandas


def identify_subgrid(data):
    """
    Identify the subgrid of an Aus400 variable

    Args:
        data: Variable to identify

    Returns:
        :obj:`str` with subgrid id of data ('t','u' or 'v')
    """
    dlat = data["latitude"].values[1] - data["latitude"].values[0]
    delta = round(dlat * 10000) / 10000

    # Subtract centre of domain
    lat_offset = data["latitude"].values[0] - -27.8
    lon_offset = data["longitude"].values[0] - 133.26

    lat_offset = numpy.mod(lat_offset, delta)
    lon_offset = numpy.mod(lon_offset, delta)

    if abs(lon_offset - delta / 2) < 0.0001:
        grid = "u"
    elif abs(lat_offset - delta / 2) < 0.0001:
        grid = "v"
    else:
        grid = "t"

    return grid


def identify_resolution(data: xarray.Dataset):
    """
    Identify the resolution of an Aus400 variable

    Args:
        data: Variable to identify

    Returns:
        :obj:`str` with resolution id of 'data'
    """

    dlat = abs(data["latitude"].values[1] - data["latitude"].values[0])

    lat_res = f"d{round(dlat*10000):04d}"

    # also consider longitude resolution in the case of cross-sectioned data
    # assuming the no. of points is automatic, at least one of lat/lon should have
    # the same resolution as before
    dlon = abs(data["longitude"].values[1] - data["longitude"].values[0])

    lon_res = f"d{round(dlon*10000):04d}"

    if lat_res not in ["d0198", "d0036"] and lon_res not in ["d0198", "d0036"]:
        raise Exception(f"Unknown grid: spacing {dlat} {dlon}")

    return max(lat_res, lon_res)


def identify_grid(data: xarray.Dataset):
    """
    Identify the grid of an Aus400 variable

    Args:
        data: Variable to identify

    Returns:
        :obj:`str` with grid id of 'data'
    """

    res = identify_resolution(data)
    grid = identify_subgrid(data)

    return f"{res}{grid}"


def to_d0198(data: xarray.Dataset):
    """
    Regrid an Aus400 variable to the 2.2km t (scalar) grid

    Args:
        data: Variable to regrid

    Returns:
        :obj:`xarray.Dataset` with 'data' on the 'd0198t' grid
    """
    grid = identify_grid(data)

    if grid == "d0198t":
        return data

    weights = xarray.open_dataset(root / "grids" / f"weights_{grid}_to_d0198t.nc")

    return regrid(data, weights=weights)


def to_barra(data: xarray.Dataset):
    """
    Regrid an Aus400 variable to the BARRA t (scalar) grid

    Args:
        data: Variable to regrid

    Returns:
        :obj:`xarray.Dataset` with 'data' on the 'barrat' grid
    """
    grid = identify_grid(data)

    if grid == "d0198t":
        return data

    weights = xarray.open_dataset(root / "grids" / f"weights_{grid}_to_barrat.nc")

    return regrid(data, weights=weights)


def regrid_vector(data):
    """
    Redrigs vector quantities like u/v defined on grid edges to the
    scalar grid on gridpoint centres (same resolution as original)

    will need to load a 'dummy' variable to get the coordinates
    of the gridpoint centres at the same resolution as input data
    - might be able to just use grids in /g/data instead?
    -- > these are actually different from the variable grids (?)

    Inputs:
        data: input data
    Outputs:
        data_regrid: regridded data
    """

    res = identify_resolution(data)

    # load the grid to reshape input data to
    # note: for now we are using pressure as a dummy variable to get the target grid
    # for some reason, the d0198t/d0036t grids are very slightly different from the
    # actual grid for these variables (offest by around 10e-6)

    # grid_path = '/g/data/ia89/aus400/grids/'
    # if res == 'd0036':
    #     grid = xr.open_dataarray(grid_path+'d0036t.nc')
    # elif res == 'd0198':
    #     grid = xr.open_dataarray(grid_path+'d0198t.nc')

    # note: dims are called lat/lon on the grid but latitude/longitude on the input
    # change this to be consistent
    # grid = grid.rename({'lat': 'latitude', 'lon': 'longitude'})

    grid = load_var(
        resolution=res,
        stream="fx",
        variable="lnd_mask",
    )

    # cut lats/lons of grid to that of input
    grid = grid.sel(latitude=slice(min(data.latitude), max(data.latitude)))
    grid = grid.sel(longitude=slice(min(data.longitude), max(data.longitude)))

    # need to squeeze input data (xr.interp_like doesn't like the exta dims for some reason)
    squeezed_dims = [dim for dim in data.dims if data[dim].size == 1]
    data = data.squeeze()

    data_regrid = data.interp_like(grid)

    # expand dims (any further vertical interpolation needs expanded dims)
    data_regrid = data_regrid.expand_dims(squeezed_dims)

    return data_regrid
