import numpy as np
import rasterio
from rasterio import features
from rasterio import mask
import fiona

shp = '/home/jonas/barriere.shp'
vrt = '/tmp/dsm/nine_cells3.vrt'
out_rst = '/tmp/dsm/rasterized.tif'

with fiona.open(shp, "r") as shapefile, rasterio.open(vrt) as src_rst:

#    dsm = src_rst.read()
    out_meta = src_rst.meta.copy()
    print(out_meta)
    out_meta.update(dtype=rasterio.int16,driver='GTiff') 
    image = features.rasterize(
		((feature['geometry'],np.int(feature['properties']['hoejde'])) for feature in shapefile),
		out_shape=src_rst.shape,
		transform=src_rst.transform,
		all_touched=True)	    
    with rasterio.open(out_rst,'w',**out_meta) as dst: 
        dst.write(image.astype(rasterio.int16), indexes=1)
# Read raster bands directly to Numpy arrays.
#

# Combine arrays in place. Expecting that the sum will
# temporarily exceed the 8-bit integer range, initialize it as
# a 64-bit float (the numpy default) array. Adding other
# arrays to it in-place converts those arrays "up" and
# preserves the type of the total array.
# total = np.zeros(r.shape)
# for band in r, g, b:
#     total += band
# total /= 3

# Write the product as a raster band to a new 8-bit file. For
# the new file's profile, we start with the meta attributes of
# the source file, but then change the band count to 1, set the
# dtype to uint8, and specify LZW compression.
# profile = src.profile
# profile.update(dtype=rasterio.uint8, count=1, compress='lzw')
# 
# with rasterio.open('example-total.tif', 'w', **profile) as dst:
#     dst.write(total.astype(rasterio.uint8), 1)
