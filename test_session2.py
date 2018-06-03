#!/usr/bin/env python
# filename: test_session.py

from grass_session import Session
from grass.script import core as gcore
import grass.script as grass
from grass.pygrass.raster import RasterRow 
import numpy as np

vrt = '/tmp/dsm/nine_cells3.vrt' 
output_tif = '/tmp/dsm/viewshed.tif'

with Session(gisdb="/tmp/grassdb_test", location="test",
             create_opts=single_tif):
    print(gcore.parse_command("g.gisenv", flags="s"))
    
    dsm = RasterRow(vrt)
    dsm.exists()
    dsm.mapset
    dsm.open('r')
    np.array(dsm)
     


# gcore.run_command('r.in.gdal', input=single_tif, output='tempdsm')
 #   gcore.run_command('r.viewshed', input='tempdsm', output='viewshed', max_distance=1000, memory=1424, coordinates=(701495,6201503), observer_elevation=500.0)
  #  gcore.run_command('r.out.gdal', input='viewshed', output=output_tif)
