#!/usr/bin/env python
import psycopg2
import argparse
import os
import subprocess
import re
from extend_file_to_files import ExtendFileToFiles

 
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="""path to tif file for which
                       calculation has to be done""")
    args = parser.parse_args()

file_obj = ExtendFileToFiles('.vrt', '/tmp/', grid_size=5, input_file=args.file)
point = tuple(e * 1000 for e in file_obj.point)
print(point)
# point = (701495,6201503)

class QueryIters():
    def __init__(self, lower_left_coord, extent):
        self.lower_left_coord = lower_left_coord
        self.extent = extent
        self.envelope = spatial_envelope(self.lower_left_coord, self.extent)
        self.query_building_w_height = """
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
                            st_setsrid( ST_MakeEnvelope(%s, %s, %s, %s),25832) )
                              group by
                                gid
                               ,geom
                               ,fot_id )
                        inputs;"""

        def spatial_envelope(self, lower_left_coord, extent):
            upper_right_coord = tuple(e + extent for e in lower_left_coord)
            return (lower_left_coord[1],lower_left_coord[0], upper_right_coord[1],
                   upper_right_coord[0])

        def connect_cursor(dbname, user, password, query, extent)
            try:
               conn = psycopg2.connect(dbname=dbname, user=user,
                                       password=password)
            except:
               print('unable to connect')

            cur = conn.cursor()

            try:
                cur.execute(query, extent)
            #    as_tuple = cur.fetchone()
                # as_dict = as_tuple[0]
            except:
                print("couldn't execute query")

            # list_of_dicts = as_dict["features"]
            for row in cur:
                print(row)
                
            print(query2)
            # print(as_tuple)
            conn.close()
