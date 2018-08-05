#!/usr/bin/env python
import argparse
import os
import subprocess
import re

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="""path to tif file for which
                        calculation has to be done""")
    args = parser.parse_args()


class ExtendFileToFiles(): ## bedre navn der er noget med at gruppere, samle, appende filer. Husk at navnet skal vaere et objekt/navneord
    def __init__(self, input_file, destination='/tmp/', grid_size=5,
                 extension='.vrt'):
        self.gdalbuildvrt = '/usr/bin/gdalbuildvrt'
        self.vrt_destination = destination
        self.input_file = input_file
        self.grid_size = grid_size
        self.filename, self.file_extension = os.path.splitext(self.input_file)
        self.abspath = os.path.dirname(self.input_file)
        self.base_name = os.path.basename(self.filename)
        self.prefix = self.base_name[0:8]
        self.base_vrt = self.base_name + extension
        self.vrt_abs = os.path.join(self.vrt_destination, self.base_vrt)
        self.pattern =  '.*(\d{4})_(\d{3}).*'
        self.point = self.x_y_from_name(self.pattern, self.base_name)
        self.extended_coordinates = self.extended_coordinates(self.grid_size,
                                                              self.point[1],
                                                              self.point[0])
        self.bbox = self.raster_bounding_box(self.extended_coordinates)
        self.extend_to_files = self.file_grid(self.prefix,
                                              self.extended_coordinates, 
                                              self.file_extension)
        self.files_as_string = self.paths_as_string()
        self.cmd_list = [self.gdalbuildvrt, '-overwrite', self.vrt_abs]
        self.cmd_as_string = ' '.join(self.cmd_list) + ' ' + self.files_as_string
	
	## alle metoder skal helst navngives som udsagnsord
    def x_y_from_name(self, pattern, name):
        matches = re.match(self.pattern, self.base_name)
        str_tuple = matches.group(1, 2)
        return tuple(int(e) for e in str_tuple) 

    def extended_coordinates(self, grid_size, x_coor, y_coor):
        grid_extent = grid_size / 2
        grid_list = [-grid_extent, grid_extent + 1]
        return [(y_coor + u, x_coor + i) 
                for i in range(*grid_list) 
                for u in range(*grid_list)]

    def raster_bounding_box(self, list_lower_left_coords): ## get_bbox
        lower_left_rast, upper_right_rast = list_lower_left_coords[0], list_lower_left_coords[-1]
        bbox = tuple([i * 1000 for i in lower_left_rast[::-1]] 
                     + [(i + 1) * 1000 for i in upper_right_rast[::-1]])
        return bbox

    def file_grid(self, prefix, coord_list, extension='.tif'):
        return [prefix
                + str(i[0])
                + '_'
                + str(i[1])
                + extension
                for i in coord_list]

    def paths_as_string(self):
        return ' '.join([os.path.join(self.abspath,i) 
                         for i in self.extend_to_files])
	
	## metode der tager subprocess og outputter vrt (build_vrt)

if __name__ == "__main__":
    file_obj = ExtendFileToFiles(args.file, '/tmp/', 5,  '.vrt', )
    print(file_obj.cmd_as_string)
    print(file_obj.file_extension)
    subprocess.call(file_obj.cmd_as_string, shell=True)
    print("vrt created as" + file_obj.vrt_abs)
    print(file_obj.bbox)
