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

import pandas
import xarray
from pathlib import Path

root = Path("/g/data/ia89/aus400")


def load_catalogue():
    cat = pandas.read_csv(root / "catalogue.csv")
    var = pandas.read_csv(root / "variables.csv")

    return cat.merge(var, on=["variable", "stream"])


catalogue = load_catalogue()


def filter_catalogue(c=catalogue, **kwargs):
    """
    Returns a filtered view of the catalogue

    By default the Aus400 catalogue is used as a starting point, if more
    complex filtering is required a different source may be provided.

    Args:
        catalogue: Source catalogue (default aus400.catalogue)
        resolution ('d0036' or 'd0198'): Resolution to select
        ensemble (int): Ensemble member to select
        stream (str): Output stream to select
        variable (str): Variable name to select

    Returns:
        A filtered view of the catalogue
    """

    for k, v in kwargs.items():
        c = c[c[k] == v]

    return c


def load_all(**kwargs):
    """
    Load multiple variables, e.g. from different streams or resolutions

    Arguments should be used to narrow down what gets loaded from the full
    catalogue

    Args:
        kwargs: See filter_catalogue

    Returns:
        Dict[str, xarray.Dataset]
    """
    c = filter_catalogue(**kwargs)

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


def load(**kwargs):
    """
    Load a single variable

    Arguments should be used to narrow down what gets loaded from the full
    catalogue

    Args:
        See filter_catalogue

    Returns:
        xarray.Dataset
    """

    results = load_all(**kwargs)

    if len(results) > 1:
        raise ValueError(
            "Selection contains multiple results, refine the filter or use the 'load_all()' function"
        )

    return list(results.values())[0]
