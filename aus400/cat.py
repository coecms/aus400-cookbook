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
Tools for filtering and loading from the Aus400 catalogue

.. py:data:: catalogue
    :type: pandas.DataFrame

    The full Aus400 catalogue, as a :class:`pandas.DataFrame`. This catalogue
    may be filtered using :meth:`filter_catalogue`, or the matching files
    opened as :obj:`xarray.Dataset` with :meth:`load` or :meth:`load_all`.

    The catalogue has the following columns:
    
    runid
        Experiment run name (e.g. u-bq574)

    resolution
        Data resolution (e.g. d0036) - A 'd' then the grid spacing in
        ten-thousandths of a degree

    ensemble
        Ensemble member

    stream
        Output stream (fx, cldrad, mdl, slv or spec)

    variable
        BARRA variable name

    time
        First timestamp in the file

    path
        Path to the file

    standard_name
        CF standard name

    description
        Description of the variable

    methods
        Variable processing
"""

import pandas
import xarray
from pathlib import Path

root = Path("/g/data/ia89/aus400")


def load_catalogue():
    if not root.exists():
        return None

    cat = pandas.read_csv(root / "catalogue.csv")
    var = pandas.read_csv(root / "variables.csv")

    return cat.merge(var, on=["variable", "stream"])


catalogue = load_catalogue()


def filter_catalogue(cat: pandas.DataFrame=catalogue, **kwargs):
    """
    Returns a filtered view of the catalogue

    By default the Aus400 catalogue is used as a starting point, if more
    complex filtering is required a different source may be provided.

    Args:
        cat: Source catalogue (default :data:`catalogue`)
        resolution ('d0036' or 'd0198'): Resolution to select
        ensemble (int): Ensemble member to select
        stream (str): Output stream to select
        variable (str): Variable name to select
        **kwargs: Any other column from :data:`catalogue`

    Returns:
        A filtered view of the catalogue
    """
    c = cat

    for k, v in kwargs.items():
        c = c[c[k] == v]

    return c


def load_all(cat: pandas.DataFrame=catalogue, **kwargs):
    """
    Load multiple variables, e.g. from different streams or resolutions

    Arguments should be used to narrow down what gets loaded from the full
    catalogue

    Args:
        **kwargs: See :meth:`filter_catalogue`

    Returns:
        Dict[str, :obj:`xarray.Dataset`], with keys named like
        "{resolution}.{stream}.{variable}"
    """
    c = filter_catalogue(cat, **kwargs)

    results = {}

    for k, g in c.groupby(["resolution", "stream", "variable"]):
        res, stream, var = k
        name = f"{res}.{stream}.{var}"

        chunks = {"latitude": 500, "longitude": 500}

        # Get the variable dimensions
        with xarray.open_dataset(root / g["path"].iloc[0], chunks={}) as sample:
            da = sample[var]
            for d in da.dims:
                if d not in chunks:
                    chunks[d] = 1

        ens = []
        dss = []

        # Load the files in each ensemble member
        for e, eg in g.groupby("ensemble"):
            paths = eg.sort_values("time")["path"].apply(lambda p: root / p)
            ds = xarray.open_mfdataset(
                paths,
                combine="nested",
                concat_dim="time",
                parallel=True,
                coords="minimal",
                compat="override",
                chunks=chunks,
            )

            ens.append(e)
            dss.append(ds)

        if len(dss) > 1:
            ds = xarray.concat(dss, dim="ensemble")
            ds["ensemble"] = ens
        else:
            ds = dss[0]

        ds.attrs["resolution"] = res
        ds.attrs["stream"] = stream

        results[name] = ds

    return results


def load(cat: pandas.DataFrame=catalogue, **kwargs):
    """
    Load a single variable

    Arguments should be used to narrow down what gets loaded from the full
    catalogue

    Args:
        **kwargs: See :meth:`filter_catalogue`

    Returns:
        :obj:`xarray.Dataset`
    """

    results = load_all(cat, **kwargs)

    if len(results) > 1:
        raise ValueError(
            "Selection contains multiple results, refine the filter or use the 'load_all()' function"
        )

    return list(results.values())[0]
