#!/usr/bin/env python
import os
import numpy as np
import rasterio
from rasterio import features
from rasterio import mask
import fiona
from grass_session import Session
from grass.pygrass.modules import Module
from grass.script import core as gcore
import psycopg2
import shutil

assigned_mem=4000
distance = 2000
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

uuoer = """
        select uuoid, st_x(geom) x, st_y(geom) y, uuoz
        from temp_jonyp.uuoer
        where fot_id = 1012269302

        """
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

cur.execute(uuoer)
uuo_result = cur.fetchall()

list_of_dicts = as_dict["features"]

shp = '/home/jonas/udsigt/barriere.shp'
vrt = '/tmp/DSM_1km_6205_705.vrt'
out_rst = '/tmp/burn_raster.tif'
burn_viewshed_rst = '/tmp/burn_viewshed_rst.tif'
grassdb = '/tmp/grassdb_test'
total_cells_output = '/tmp/count.txt'

grass_locdir = 'wd_' + 'bygningsid' 
# str(uuo_result[0])
## for tif der indeholder mere en x, opret 4 symlinks med 500m celle navne
## soerg for at regex kan handtere flere cifre
    
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
# print(np_array)
print(uuo_result)

def calc_view(grassdb, location_dir, raster_meta, numpy_array, distance,
              id_lat_lon_z):
    """calculates a viewshed. Requires:
        - grassdb, path to where Grass can establish a folder structrure
        - location_dir, folder within grassdb
        - raster_meta, geo-raster metadata supplied to Grass. Adopted by output
        - numpy_array, adopts the raster_meta to become geo-aware:)
        - distance, radius to calculate visibility within
        - id_lat_lon_z, list of tuples containing: 
          - an unique id
          - latitutude as numeric
          - longtitude as numeric
          - z height
    """
    with Session(gisdb=grassdb, location=location_dir, create_opts=raster_meta):
        import grass.script.array as garray

        r_viewshed = Module('r.viewshed')
        r_out_gdal = Module('r.out.gdal')
        r_stats = Module('r.stats')
        r_univar = Module('r.univar')
        from_np_raster = garray.array()
        from_np_raster[...] = numpy_array
        from_np_raster.write('ny_rast',overwrite=True)
        # print(from_np_raster)


        
        for uuo in id_lat_lon_z:
            viewshedname = 'vs_' + str(uuo[0])
            out_filepath = '/tmp/' + viewshedname
            from_position = (uuo[1], uuo[2])
            print(from_position)
            z = uuo[3]
            count_out = '/tmp/' + 'cnt_'  + str(uuo[0]) + '.txt'
            message_crt = 'Creating viewshed {}, position is {} and height is {}'
            creating = message_crt.format(viewshedname, str(from_position),
                                          str(z))
            print(creating)
            r_viewshed(input='ny_rast', overwrite=True, output=viewshedname,
                       max_distance=distance, memory=2560, 
                       coordinates=from_position, observer_elevation=z)
            r_stats(flags='nc',overwrite=True,input=viewshedname, 
                    output=count_out)
            ## finde ud af hvordan r_stats kan outputte til noget som
            ## python kan laese direkte
            message_rst_out = 'Writing viewshed {} to file {}'
            writing_rst = message_rst_out.format(viewshedname, out_filepath) 
            print(writing_rst)
            r_out_gdal(overwrite=True, input=viewshedname, output=out_filepath)
        workdir = grassdb + '/' + location_dir
        message_rm_dir = 'removing directory {}'.format(workdir)
        print(message_rm_dir)
        shutil.rmtree(workdir)

# calc_view(grassdb, grass_locdir, vrt, np_array, distance, uuo_result)
pth = os.path.join(grassdb, grass_locdir)
print(pth)

def sum_column_from_file(file_name, column_index):
    """from file with column structure (blank space separated) summarize the
    column at the index given.
    requires:
        - path to file with column structure
        - index of column with numeric values
    returns:
        - the sum of the column
    """
    counts = []
    with open(file_name) as column_file:
        for line in column_file:
            number = int(line.split()[column_index])
            counts.append(number)
    return sum(counts)

# cnt = sum_column_from_file(total_cells_output, -1)
# print(cnt)
## tilfoej funktion der deleter grass-db'en

