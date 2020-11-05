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

from ..vertical import *
from ..cat import load


def test_to_plev():
    ds = load(
        resolution="d0198",
        stream="mdl",
        variable="air_temp",
        ensemble=0,
        time="20170328T1200",
    )

    ds_p = to_plev(ds["air_temp"], [10000])

    assert "pressure" in ds_p.dims
    assert ds_p["pressure"].size == 1
