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

"""
XGCM representations of Aus400 grids
"""

from .cat import root
import xarray
import xgcm

def grid_from_id(g):
    """
    XGCM representation of Aus400 grid 'g'
    """

    res = g[:5]
    subt = g[-1]

    ds = xarray.open_dataset(root / "grids" / f"{g}.nc")

    coords = {
        'X': {'center': 'longitude'},
        'Y': {'center': 'latitude'},
        }

    if subt == 'u':
        coords['X'] = {'left': 'longitude'}
    elif subt == 'v':
        coords['Y'] = {'left': 'latitude'}

    return xgcm.Grid(ds, coords)


def grid(ds):
    """
    XGCM grid of Aus400 variable 'ds'
    """
    
    coords = {
        'X': {'center': 'latitude'},
        'Y': {'center': 'latitude'},
        }

    if 'model_level_number' in ds.coords:
        coords['Z'] = {'center': 'model_level_number'}

    return xgcm.Grid(ds, coords=coords, periodic=False)
