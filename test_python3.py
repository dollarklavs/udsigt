import os

# import grass_session
from grass_session import Session

# import grass python libraries
from grass.pygrass.modules.shortcuts import general as g


# set some common environmental variables, like:
os.environ.update(dict(GRASS_COMPRESS_NULLS='1',
                       GRASS_COMPRESSOR='ZSTD'))

# create a PERMANENT mapset
# create a Session instance
PERMANENT = Session()
PERMANENT.open(gisdb='/tmp', location='grassdb_test',
               create_opts='EPSG:25832')


# execute some command inside PERMANENT
g.mapsets(flags="l")
g.list(type="raster", flags="m")

# exit from PERMANENT
PERMANENT.close()

# create a new mapset in the same location
user = Session()
user.open(gisdb='/tmp', location='mytest', mapset='user',
               create_opts='')

# execute some command inside user
g.mapsets(flags="l")
g.list(type="raster", flags="m")

# exit from user
user.close()
