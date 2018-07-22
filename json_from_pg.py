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

query_building_w_height2 = """
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
                    st_setsrid( ST_MakeEnvelope({}, {}, {}, {}),25832) )
                      group by
                        gid
                       ,geom
                       ,fot_id )
                inputs;"""

query_building_w_height = """
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

class QueryIters():
    def __init__(self, lower_left_coord, extent, query):
        self.lower_left_coord = lower_left_coord
        self.extent = extent
        self.envelope = self.spatial_envelope(self.lower_left_coord, self.extent)
        print(self.envelope)
        self.query = query.format(*self.envelope)
        self.conn = psycopg2.connect(dbname='jonas', user='jonas',
                                password='logger')
        self.cur = self.conn.cursor()
        print(self.cur.mogrify(self.query, self.envelope)
        self.results = self.cur.execute(self.query, self.envelope)
        print(type(self.results))

    def spatial_envelope(self, lower_left_coord, extent):
        upper_right_coord = tuple(e + extent for e in lower_left_coord)
        return (lower_left_coord[1],lower_left_coord[0], upper_right_coord[1],
               upper_right_coord[0])

#     def __enter__(self):
#         self.conn = psycopg2.connect(dbname='jonas', user='jonas',
#                                 password='logger')
#         self.cur = self.conn.cursor()
#         print(self.cur.mogrify(self.query, self.envelope))
#         self.results = self.cur.execute(self.query, self.envelope)
#         print(type(self.results))
# 
#     def __iter__(self):
#         for result in self.results:
#             yield result
# 
#     def __exit__(self, exc_type, exc_value, exc_traceback):
#         self.conn.close()

file_obj = ExtendFileToFiles('.vrt', '/tmp/', grid_size=5, input_file=args.file)
point = tuple(e * 1000 for e in file_obj.point)

json = QueryIters(point, 1000, query_building_w_height)
for j in json:
    print(j)
