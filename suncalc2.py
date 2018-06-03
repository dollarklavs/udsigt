#!/usr/bin/env python

from grass_session import Session
from grass.script import core as gcore
import grass.script as grass
import grass.pygrass
from grass.pygrass.modules import Module    # import Module from PyGRASS


single_tif = '/tmp/dsm/nine_cells3.vrt' 
output_tif = '/tmp/dsm/suncalc.tif'
barriere_shp = '/home/jonas/barriere.shp'
# '/tmp/dsm/DSM_1km_6200_701.tif'

# create a new location from EPSG code (can also be a GeoTIFF or SHP or ... file)
# 27.marts2018, 36sek for en tif (viewshed for hele 1km celle?)
with Session(gisdb="/tmp/grassdb_test", location="test",
             create_opts=single_tif):
    print(gcore.parse_command("g.gisenv", flags="s"))
   # do something in permanent
    gcore.run_command('r.in.gdal', input=single_tif, output='tempdsm')
    r_sun = Module('r.sun')
    r_slope_aspect = Module('r.slope.aspect')
    r_horizon = Module('r.horizon')
    
    r_horizon(elevation='tempdsm', step=30, output='horizon_angle')
    r_slope_aspect(elevation='tempdsm', aspect='aspect', slope='slope')
    r_sun(elevation='tempdsm', horizon_basename='horizon_angle', horizon_step=30, aspect='aspect', slope='slope', glob_rad='global_rad', day=180, time=14) 
#    grass.sun
