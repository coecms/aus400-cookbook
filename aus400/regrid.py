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
from .cat import root


def identify_grid(data: xarray.Dataset):
    """
    Identify the grid of an Aus400 variable

    Args:
        data: Variable to identify

    Returns:
        :obj:`str` with grid id of 'data'
    """
    res = data.attrs["resolution"]
    grid = "t"

    return f"{res}{grid}"


def to_d0198(data: xarray.Dataset):
    """
    Regrid an Aus400 variable to 2.2km

    Args:
        data: Variable to identify

    Returns:
        :obj:`xarray.Dataset` with 'data' on the 'd0198t' grid
    """
    grid = identify_grid(data)

    if grid == "d0198t":
        return data

    weights = xarray.open_dataset(root / "grids" / f"weights_{grid}_to_d0198t.nc")

    return regrid(data, weights=weights)
