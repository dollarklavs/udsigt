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
                        st_setsrid( ST_MakeEnvelope(701000, 6201000, 702000,
                        6202000),25832) )
                          group by
                            gid
                           ,geom
                           ,fot_id )
                    inputs)
            features;"""
try:
   conn = psycopg2.connect(dbname='jonas', user='jonas', password='logger')
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
vrt = '/tmp/dsm/nine_cells3.vrt'
out_rst = '/tmp/dsm/burn_raster.tif'
burn_viewshed_rst = '/tmp/dsm/burn_viewshed_rst.tif'
grassdb = '/tmp/grassdb_test'

assigned_mem=4000
distance = 2000
observer_height = 10
point = (701495,6201503)

def viewshed(vrt,list_of_dicts,distance,point,observer_height,burn_viewshed_rst)
    with rasterio.open(vrt) as src_rst:

        dsm = src_rst.read()
        out_meta = src_rst.meta.copy()
        print(out_meta)
        out_meta.update(dtype=rasterio.int16,driver='GTiff') 
        mask = features.geometry_mask(
                                      [feature["feature"]["geometry"] for feature in
                                       list_of_dicts],
                                       src_rst.shape,
                                       transform=src_rst.transform,
                                       all_touched=True, 
                                       invert=True)
        new_dsm = np.copy(np.squeeze(dsm)) #Forstaer ikke hvorfor, men dsm'en har en ekstra dimension, 
                                           #som jeg fjerner med squeeze, saa den passer med result dsm'en
        with rasterio.Env():
            result = features.rasterize(
                                        ((feature['feature']['geometry'],np.int(feature['feature']['properties']['hoejde'])
                                         * 1000)
                                          for feature in list_of_dicts), 
                                          out_shape=src_rst.shape,
                                          transform=src_rst.transform,
                                          all_touched=True)             
            new_dsm[mask] = result[mask] 

            with Session(gisdb=grassdb, location="test",create_opts=vrt):
                import grass.script.array as garray
                r_viewshed = Module('r.viewshed')
                r_out_gdal = Module('r.out.gdal')
                r_stats = Module('r.stats')
                from_np_raster = garray.array()
                from_np_raster[...] = new_dsm
                from_np_raster.write('ny_rast',overwrite=True)
                print(from_np_raster)
                gcore.run_command('r.viewshed', overwrite=True, memory=assigned_mem, input='ny_rast', output='viewshed', max_distance=distance, coordinates=point, observer_elevation=observer_height)
                visible_cells = r_stats(flags='nc',in='viewshed')
                #r_viewshed(input=from_np_raster, output='viewshed', max_distance=1000, memory=1424, coordinates=(701495,6201503), observer_elevation=500.0)
                r_out_gdal(overwrite=True, input='viewshed', output=burn_viewshed_rst)
    return visible_cells
    #    with rasterio.open(out_rst,'w',**out_meta) as dst: 
    #        dst.write(new_dsm.astype(rasterio.int16), 1)

