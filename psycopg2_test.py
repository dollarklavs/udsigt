import psycopg2
import json
import ast

query_string = """
              select 
                fot_id
               ,avg(hoejde) hoejde
               ,st_asgeojson(geom) geom
              from 
               (select 
                  fot_id
                 ,st_z((st_dumppoints(geom)).geom) hoejde
                 ,geom
                from temp_jonyp.nye_bygninger limit 10
               ) foo 
               group by 
                 fot_id
                ,geom
                """
query2 = """SELECT 
              jsonb_build_object(
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
                                              from temp_jonyp.nye_bygninger ) foo 
                                              where st_intersects(foo.geom,
                                              st_setsrid(ST_MakeEnvelope(701000,
                                              6201000, 702000, 6202000),25832))
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
cur.execute(query2)
as_tuple = cur.fetchone()
# json_row_str = json_row[0].decode("utf-8")
# print(json_row)
as_str = as_tuple[0]
# as_dict = ast.literal_eval(as_str)
# print(as_str["features"])
for i in as_str["features"]:
    print(i["feature"]["geometry"])
    print(i["feature"]["properties"]["hoejde"])
#for k, v in as_dict.iteritems():
#    print('{} : {} \n\n\n'.format( k , v))
   
# print(as_json)

# for record in cur:
#     print(record[0])
