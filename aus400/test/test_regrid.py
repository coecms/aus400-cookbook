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

from ..regrid import *
from ..cat import load

def test_id_grid():
    ds = load(resolution='d0036', stream='spec', variable='sfc_temp', ensemble=0, time='20170328T1200')

    assert identify_grid(ds) == 'd0036t'
    assert identify_grid(ds['sfc_temp']) == 'd0036t'

    ds = load(resolution='d0036', stream='spec', variable='uwnd10m', ensemble=0, time='20170328T1200')

    assert identify_grid(ds) == 'd0036u'
    assert identify_grid(ds['uwnd10m']) == 'd0036u'

    ds = load(resolution='d0036', stream='spec', variable='vwnd10m', ensemble=0, time='20170328T1200')

    assert identify_grid(ds) == 'd0036v'
    assert identify_grid(ds['vwnd10m']) == 'd0036v'

    ds = load(resolution='d0198', stream='spec', variable='vwnd10m', ensemble=0, time='20170328T1200')

    assert identify_grid(ds) == 'd0198v'
    assert identify_grid(ds['vwnd10m']) == 'd0198v'


def test_to_d0198():
    ds = load(resolution='d0036', stream='spec', variable='uwnd10m', ensemble=0, time='20170328T1200')

    ds = to_d0198(ds)

    assert identify_grid(ds) == 'd0198t'


def test_to_t():
    ds = load(resolution='d0036', stream='spec', variable='uwnd10m', ensemble=0, time='20170328T1200')

    ds = to_t(ds)

    assert identify_grid(ds) == 'd0036t'

