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
Functions for rendering Aus400 data using Pillow
"""

import PIL
from typing import Tuple

def to_bytes(array):
    """
    Convert an array of floats between 0 and 1 to bytes between 0 and 255
    """
    return (array * (2**8-1)).astype('uint8')


def field_to_image(field: xarray.DataArray, vmin: float=None, vmax: float=None):
    """
    Render a Aus400 field as an image

    If vmin, vmax are not provided they are set to the minimum, maximum of the
    field. Values outside of vmin, vmax are clipped.

    Args:
        field: Input 2d field
        vmin: Minimum value for normalisation
        vmax: Maximum value for normalisation

    Returns:
        PIL.Image in mode 'L'
    """

    if field.ndim != 2:
        raise Exception("Expected a 2d field")

    if vmin is None:
        vmin = field.min().values

    if vmax is None:
        vmax = field.max().values

    normalised_field = numpy.clip((field - vmin)/(vmax - vmin), 0, 1)
    byte_field = to_bytes(normalised_field)

    return (PIL.Image.fromarray(byte_field.values, mode='L')
		.transpose(PIL.Image.FLIP_TOP_BOTTOM))


def set_image_mpl_cmap(image: PIL.Image, cmap: str):
    """
    Set a PIL.Image to use a matplotlib colour map
    
    See https://matplotlib.org/3.1.1/gallery/color/colormap_reference.html

    Args:
        image: Image to modify in-place
        cmap: Matplotlib colour map name
    """
    cmap = plt.get_cmap(cmap)
    value_levels = numpy.linspace(0,1,2**8)
    pallet = to_bytes(cmap(value_levels))[:,0:3]
    image.putpalette(pallet, 'RGB')


def zoom_region(image: PIL.Image, lat: float, lon: float, scale: float, size: Tuple[int, int]):
    """
    Zooms to a specific region of an Aus400 rendered image

    The output image is 'scale' degrees wide, with the height determined by the
    aspect ratio of 'size'

    Args:
        image: Source image, must cover the full d0036t grid
        lat: Central latitude
        lon: Central longitude
        scale: Output longitude width in degrees
        size: Output image size

    Returns:
        PIL.Image with size 'size'
    """

    if image.size != (13194, 10554):
        raise Exception("Input image has unexpected size, make sure it is on the d0036t grid")

    # Maintain output aspect ratio
    lat_scale = scale / size[0] * size[1]

    lon0 = lon - scale/2
    lon1 = lon + scale/2

    lat0 = lat - lat_scale/2
    lat1 = lat + lat_scale/2

    x0 = int((lon0 - 109.5106)/0.0036)
    x1 = int((lon1 - 109.5106)/0.0036)

    y0 = int((-8.8064 - lat0)/0.0036)
    y1 = int((-8.8064 - lat1)/0.0036)

    return image.transform(size=size,
            method=PIL.Image.QUAD,
            data=(x0,y1,x0,y0,x1,y0,x1,y1),
            resample=PIL.Image.BICUBIC,
            fillcolor=(0,0,0,255))
