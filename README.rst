aus400-cookbook
===============

.. image:: https://readthedocs.org/projects/aus400-cookbook/badge/?version=latest
    :target: https://aus400-cookbook.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation
.. image:: https://zenodo.org/badge/288881176.svg
    :target: https://zenodo.org/badge/latestdoi/288881176
    :alt: DOI

Notebooks and library for working with Aus400 data 

Aus400 is a large-scale high resolution simulation of the atmosphere over the
Australian continent during the landfall of Tropical Cyclone Debbie, from
20170327 to 20170329 run at NCI by the ARC Centre of Excellence for Climate
Extremes and the Bureau of Meterology for the testing of the Gadi
supercomputer.

This cookbook provides tools for working with the 50 TB of output produced by
the model run. It is intended to be run at NCI facilities, either on the VDI
virtual desktop or on the Gadi compute nodes.

The directory 'aus400' contains a library with helper functions for loading
data as Xarray objects with appropriate Dask chunking.  Documentation is
available at https://aus400-cookbook.readthedocs.io.

The 'notebooks' directory contains sample analyses of the dataset using these
functions and the `'analysis3' conda environment
<http://climate-cms.wikis.unsw.edu.au/Conda>`_ managed by CLEX CMS at NCI

`Contributions
<https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests>`_
to this repository of functions or notebooks are welcome.

Sample Notebooks
----------------

`Introduction to the Cookbook <https://nbviewer.jupyter.org/github/coecms/aus400-cookbook/blob/master/notebooks/Introduction.ipynb>`_

`Rendering the 400m domain using pillow <https://nbviewer.jupyter.org/github/coecms/aus400-cookbook/blob/master/notebooks/Rendering.ipynb>`_

`Vertical Interpolation <https://nbviewer.jupyter.org/github/coecms/aus400-cookbook/blob/master/notebooks/VerticalInterpolation.ipynb>`_

`Cross Sections <https://nbviewer.jupyter.org/github/coecms/aus400-cookbook/blob/master/notebooks/CrossSection.ipynb>`_

Using the Cookbook
------------------

Download the repository to Gadi or VDI::

    git clone https://github.com/coecms/aus400-cookbook

Open a Jupyter notebook (e.g. using `gadi_jupyter or vdi_jupyter.py <https://github.com/coecms/nci_scripts>`_)

Navigate to the repository's notebooks directory, and start your notebook with::

    import sys
    sys.path.append('../')
    import aus400
