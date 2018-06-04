#!/usr/bin/env python
import numpy as np
import rasterio
from rasterio import features
from rasterio import mask
import fiona
from grass_session import Session
from grass.pygrass.modules import Module
from grass.script import core as gcore
import psycopg2

shp = '/home/jonas/udsigt/barriere.shp'
vrt = '/tmp/dsm/nine_cells3.vrt'
out_rst = '/tmp/dsm/burn_raster.tif'
burn_viewshed_rst = '/tmp/dsm/burn_viewshed_rst.tif'
grassdb = '/tmp/grassdb_test'

assigned_mem=4000
distance = 2000
observer_height = 10
point = (701495,6201503)

with fiona.open(shp, "r") as shapefile:
    print(shapefile)
    for f in shapefile:
        print(f)
