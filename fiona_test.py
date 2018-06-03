import numpy as np                                                                              
import rasterio                                                                                 
import fiona                                                                                    
                                                                                                
shp = '/home/jonas/barriere.shp'                                                                
vrt = '/tmp/dsm/nine_cells3.vrt'                                                                
                                                                                                
with fiona.open(shp, "r") as shapefile:
   for f in shapefile:
       print(f['properties']['hoejde'])
