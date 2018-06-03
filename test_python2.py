#!/usr/bin/env python
import os
from grass_session import Session
from grass.script import core as gcore

from grass.pygrass.modules.shortcuts import general as g
from grass.pygrass.modules.shortcuts import raster as r

home= "/tmp/grassdb_test/test"
gisdb= "/tmp/grassdb_test"
loc= "test"
maps= "elevation"
epsg= "EPSG:25832"

if not os.path.exists(gisdb):
    os.makedirs(gisdb)

if not os.path.exists(os.path.join(gisdb, loc)):
with Session(gisdb=gisdb, location=loc, create_opts=epsg):
    print("Created a new location!")
else:
    print("Location already exist!")

with Session(gisdb=gisdb, location=loc, mapset="elevation", create_opts=""):
    gisenvironment = gcore.parse_command("g.gisenv", flags="s")
    print(gisenvironment)
