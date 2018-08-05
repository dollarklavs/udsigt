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

assigned_mem=4000
distance = 100
observer_height = 10
point = (705500,6205500)


query = """SELECT jsonb_build_object(                                                                                          
'type',     'FeatureCollection',
    'features', jsonb_agg(features)
        )
            FROM (
                SELECT jsonb_build_object(
                      'type',       'Feature',
                          'id',         gid,
                      'geometry',   ST_AsGeoJSON(geom)::jsonb,
                          'properties', to_jsonb(inputs) - 'gid' -
                          'geom'
                            ) AS feature
                  FROM (
                        SELECT
                          gid
                         ,geom
                         ,fot_id
                         ,avg(hoejde) hoejde
                        FROM (
                                  select
                                    gid
                                   ,geom
                                   ,fot_id
                                   ,st_z((st_dumppoints(geom)).geom ) hoejde
                                  from temp_jonyp.nye_bygninger) foo
                        where st_intersects(foo.geom,
                        st_setsrid( ST_MakeEnvelope(703000, 6203000, 708000,
                        6208000),25832) )
                          group by
                            gid
                           ,geom
                           ,fot_id )
                    inputs)
            features;"""
try:
   conn = psycopg2.connect(dbname='geotest', user='jonas', password='jonas')
except:
   print('unable to connect')

cur = conn.cursor()

try:
    cur.execute(query)
    as_tuple = cur.fetchone()
    as_dict = as_tuple[0]
except:
    print("couldn't execute query")

list_of_dicts = as_dict["features"]

shp = '/home/jonas/udsigt/barriere.shp'
vrt = '/tmp/DSM_1km_6205_705.vrt'
out_rst = '/tmp/burn_raster.tif'
burn_viewshed_rst = '/tmp/burn_viewshed_rst.tif'
grassdb = '/tmp/grassdb_test'
total_cells_output = '/tmp/count.txt'

    
def mask_rast_from_geom(raster_file, geom_iterator):
    """Returns a numpy mask of the same dimensions as the input raster and also
    a numpy array copy of the input raster.
    
    requires inputs:
        - (gdal) raster file
        - iterator of json like geometries
    returns:
        - a (numpy) raster mask
        - a numpy array copy of the input raster (should be handled elsewhere?)
    """

    with rasterio.open(raster_file) as src_rst:

        dsm = src_rst.read()
        out_meta = src_rst.meta.copy()
        print(out_meta)
        out_meta.update(dtype=rasterio.int16,driver='GTiff') 
        mask = features.geometry_mask(
                                      [feature["feature"]["geometry"] for feature in
                                      geom_iterator ],
                                       src_rst.shape,
                                       transform=src_rst.transform,
                                       all_touched=True, 
                                       invert=True)
        new_dsm = np.copy(np.squeeze(dsm)) #Forstaer ikke hvorfor, men dsm'en har en ekstra dimension, 
                                           #som jeg fjerner med squeeze, saa den passer med result dsm'en

        return mask, new_dsm

numpy_mask, numpy_raster = mask_rast_from_geom(vrt, list_of_dicts) 
print(numpy_mask, numpy_raster)

def burn_rast_from_geom(json_iter, numpy_array, numpy_mask):
    ## deles op - anden funktion, maaske
    with rasterio.Env():
        result = features.rasterize(
                                    ((feature['feature']['geometry'],np.int(feature['feature']['properties']['hoejde'])
                                     * 1000)
                                      for feature in json_iter), 
                                      out_shape=numpy_array.shape,
#                                      transform=raster.transform,
                                      all_touched=True)             
        numpy_array[numpy_mask] = result[numpy_mask] 
        return numpy_array

np_array = burn_rast_from_geom(list_of_dicts, numpy_raster, numpy_mask) 
print(np_array)

def calc_view(grassdb, location_dir, raster_meta, numpy_array, distance,
              observer_height, from_position, burn_viewshed_rst):
    ## deles op - tredje funktion
    with Session(gisdb=grassdb, location=location_dir, create_opts=raster_meta):
        import grass.script.array as garray
        r_viewshed = Module('r.viewshed')
        r_out_gdal = Module('r.out.gdal')
        r_stats = Module('r.stats')
        r_univar = Module('r.univar')
        from_np_raster = garray.array()
        from_np_raster[...] = numpy_array
        from_np_raster.write('ny_rast',overwrite=True)
        print(from_np_raster)
        gcore.run_command('r.viewshed', overwrite=True, memory=2000, 
input='ny_rast', output='viewshed', max_distance=distance, 
coordinates=from_position, observer_elevation=observer_height)
        r_stats(flags='nc',overwrite=True,input='viewshed',output=total_cells_output)
        ## finde ud af hvordan r_stats kan outputte til noget som
        ## python kan laese direkte

        counts = []
        with open(total_cells_output) as tcls:
            for line in tcls:
                nbr = int(line.split()[-1])
                counts.append(nbr)
        # summary = r_univar(map='viewshed')
        #r_viewshed(input=from_np_raster, output='viewshed', max_distance=1000, memory=1424, coordinates=(701495,6201503), observer_elevation=500.0)
        r_out_gdal(overwrite=True, input='viewshed', output=burn_viewshed_rst)
        return sum(counts) #visible_cells
    #    with rasterio.open(out_rst,'w',**out_meta) as dst: 
    #        dst.write(new_dsm.astype(rasterio.int16), 1)
cnt = calc_view(grassdb, 'test', vrt, np_array, distance, observer_height,
                point, burn_viewshed_rst)
print(cnt)
## tilfoej funktion der deleter grass-db'en

