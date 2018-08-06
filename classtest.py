#!/usr/bin/env python
import argparse
import os
import subprocess
import re
from classrewrite_dkcell import DkGridCell 


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", help="""path to tif file for which
                    calculation has to be done""")
parser.add_argument("-t", "--type", help="""type of cell, which subdivide
                    should reduce to""")
args = parser.parse_args()

cellobject = DkGridCell(args.file)
print(cellobject.abs_filename,cellobject.cell_type,cellobject.cell_id,cellobject.extent)
print(cellobject.ll_coord)
list_of_files = cellobject.subdivide(args.type)
cellobject.get_neigbouring_coords(5)
print(list_of_files)
neighbors = (cellobject.neigh_coords)
neighfiles = (cellobject.neigh_files)
cellobject.raster_bounding_box()
print(cellobject.bbox_ll, cellobject.bbox_ur)
print(cellobject.abs_path)
path = cellobject.abs_path
pathified = cellobject.pathify_file(path, neighfiles)
for i, f in enumerate(pathified):
    print(i + 1, f)
