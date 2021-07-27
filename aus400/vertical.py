#!/g/data/hh5/public/apps/nci_scripts/python-analysis3
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

from .cat import load_var
from . import xgcm
from .regrid import identify_resolution, identify_subgrid
import xarray
import pandas
from .cross_sec import cross_sec


def vertical_interp(
    ds: xarray.DataArray, source: xarray.DataArray, target
) -> xarray.DataArray:
    """
    Vertically interpolate the data in ds to the levels of 'target'

    See also: :func:`to_plev`, :func:`to_height`

    Args:
        da: Aus400 variable to regrid
        source: Aus400 variable with the source level values (e.g.
            pressure, height)
        target: Target levels to regrid to

    Returns:
        :obj:`xarray.DataArray` on the target levels
    """

    grid = xgcm.grid(ds)
    source = match_slice(source, ds)

    ds = ds.chunk({"model_level_number": None})
    source = source.chunk({"model_level_number": None})

    return grid.transform(ds, "Z", target, target_data=source)


def to_plev(ds, levels):
    """
    Interpolate the data in ds to the supplied pressure levels

    Args:
        da: Aus400 variable to regrid
        target: Target levels to regrid to

    Returns:
        :obj:`xarray.DataArray` on the target levels
    """

    res = identify_resolution(ds)
    sub = identify_subgrid(ds)

    if sub != "t":
        raise Exception(
            f"Can't vertically regrid data on '{sub}' grid, regrid to 't' first"
        )

    pressure = load_var(
        resolution=res,
        stream="mdl",
        variable="pressure",
        time=slice(
            pandas.offsets.Hour().rollback(ds["time"].values[0])
            - pandas.offsets.Hour(),
            pandas.offsets.Hour().rollback(ds["time"].values[-1])
            + pandas.offsets.Hour(),
        ),
        ensemble=slice(ds["ensemble"].values[0], ds["ensemble"].values[-1]),
    )

    # may need to c.s. data if the input is also c.s.
    if "horz_dim" in ds.dims:
        x0, x1 = ds["longitude"].values[0], ds["longitude"].values[-1]
        y0, y1 = ds["latitude"].values[0], ds["latitude"].values[-1]
        pressure = cross_sec(pressure, x0, y0, x1, y1)

    # align datasets (match_slice should handle this but sometimes problems occur
    # after regridding)
    pressure, ds = xarray.align(pressure, ds)        

    return vertical_interp(ds, pressure, levels)


def to_height(ds, levels):
    """
    Interpolate the data in ds to the supplied height levels

    Args:
        da: Aus400 variable to regrid
        target: Target levels to regrid to

    Returns:
        :obj:`xarray.DataArray` on the target levels
    """

    res = identify_resolution(ds)
    sub = identify_subgrid(ds)

    if sub != "t":
        raise Exception(
            f"Can't vertically regrid data on '{sub}' grid, regrid to 't' first"
        )

    height = load_var(resolution=res, stream="fx", variable="height_rho")

    # may need to c.s. data if the input is also c.s.
    if "horz_dim" in ds.dims:
        x0, x1 = ds.longitude.values[0], ds.longitude.values[-1]
        y0, y1 = ds.latitude.values[0], ds.latitude.values[-1]
        height = cross_sec(height, x0, y0, x1, y1)

    # align datasets (match_slice should handle this but sometimes problems occur
    # after regridding)
    height, ds = xarray.align(height, ds)        

    return vertical_interp(ds, height, levels)


def match_slice(da, target):
    """
    Match da to the slicing of target
    """

    return da.sel({d: target[d] for d in da.dims})
