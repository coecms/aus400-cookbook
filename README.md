# aus400-cookbook
Notebooks and library for working with Aus400 data

Aus400 is a large-scale high resolution simulation of the atmosphere over the Australian continent during the landfall of 
Tropical Cyclone Debbie, from 20170327 to 20170329 run at NCI by the ARC Centre of Excellence for Climate Extremes and the
Bureau of Meterology for the testing of the Gadi supercomputer.

This cookbook provides tools for working with the 50 TB of output produced by the model run. It is intended to be run at NCI
facilities, either on the VDI virtual desktop or on the Gadi compute nodes.

The directory 'aus400' contains a library with helper functions for loading data as Xarray objects with appropriate Dask chunking

## Sample Notebooks

[Introduction to the Cookbook](https://nbviewer.jupyter.org/github/coecms/aus400-cookbook/blob/master/notebooks/Introduction.ipynb)
