#!/usr/bin/env python

from grass_session import Session
from grass.script import core as gcore
import grass.script as grass
import grass.pygrass

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
    # gcore.run_command('v.import', input=barriere_shp, output='barriere')
    # gcore.run_command('v.to.rast', input='barriere', output='barriere_raster',attribute_column = 'hoejde')   
    gcore.run_command('r.sunmask', elevation='tempdsm', output='sunmask', year=2018, month=4, day=22, hour=17, minute=15, second=0, timezone=2)
    gcore.run_command('r.out.gdal', input='sunmask', output=output_tif)
# {u'GISDBASE': u"'/tmp/';",
#  u'LOCATION_NAME': u"'epsg3035';",
#  u'MAPSET': u"'PERMANENT';",}

# create a new mapset in an existing location
# with Session(gisdb="/home/jonas/Documents/grass_test", location="DSM_620_70_TIF_UTM32-ETRS89", mapset="test", create_opts=""):
    # do something in the test mapset.
#    print(gcore.parse_command("g.region", raster="DSM_1km_6200_701.tif", flags="p"))         
#    gcore.run_command('r.viewshed', input='DSM_1km_6200_701.tif', output='temp.tif', coordinates=(701420,6200542), observer_elevation=2.0)
# {u'GISDBASE': u"'/tmp/';",
#  u'LOCATION_NAME': u"'epsg3035';",
#  u'MAPSET': u"'test';",}
# g.region raster=elev_lid792_1m -p
# r.viewshed input=elev_lid792_1m output=elev_lid792_1m_viewshed coordinates=638728,220609 observer_elevation=5.0
