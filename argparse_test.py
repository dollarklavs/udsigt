#!/usr/bin/env python
import argparse
import os
import subprocess
import re

gdalbuildvrt = '/usr/bin/gdalbuildvrt'
vrt_destination = '/tmp/dsm/'

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", help="""path to tif file for which
                    calculation has to be done""")
args = parser.parse_args()

filename, file_extension = os.path.splitext(args.file)
abspath = os.path.dirname(args.file)
base_name = os.path.basename(filename)
base_vrt = base_name + '.vrt'
vrt_abs = os.path.join(vrt_destination,base_vrt)

def x_y_from_name(fn):
    pattern = '.*(\d{4})_(\d{3}).*'
    matches = re.match(pattern,fn)
    return matches.group(1,2)

def file_grid(prefix,x_coor,y_coor,extension='.tif',grid_size=5):
    grid_extent = grid_size / 2
    grid_list = [-grid_extent,grid_extent + 1]
    return [prefix + str(y_coor + u) + '_' + str(x_coor + i) +
            extension for i in
            range(*grid_list) for u in range(*grid_list)]


point = x_y_from_name(base_name)
tif_grid = file_grid('DSM_1km_',int(point[1]),int(point[0]))
tif_grid_abs = [os.path.join(abspath,i) for i in tif_grid]
tif_grid_string = ' '.join([os.path.join(abspath,i) for i in tif_grid])


full_cmd_list = [gdalbuildvrt, '-overwrite', vrt_abs,
                 tif_grid_string]
cmd_and_tifs = full_cmd_list + tif_grid_abs
cmd_string = ' '.join(cmd_and_tifs)
subprocess.call(cmd_string, shell=True)
