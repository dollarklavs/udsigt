#!/usr/bin/env python
import argparse
import os
import subprocess
import re

class DkGridCell():

# class variable with the cell type-id as key. The value is a list containing the extent
# in meter and substr_slice, used as index from end of base filename to get the
# cell identifier.
    cell_types_data = {'100km': 
                      [{extent : 100000}, 
                       {substr_slice : -4}], 
                      '10km':
                      [{extent : 10000}, 
                       {substr_slice : -6}], 
                      '1km' : 
                      [{extent : 1000}, 
                       {substr_slice : -8}], 
                      '500m' : 
                      [{extent : 500},
                       {substr_slice : -10}],
                      '250m' : 
                      [{extent : 250}, 
                       {substr_slice : -12}], 
                      '100m' :
                      [{extent : 100}, 
                       {substr_slice : -10}]
                      }
 
    def __init__(self, file_name):
        self.cell_type, self.cell_id, self.extent =
        type_id_extent_from_file(file_name)
        
    def type_id_extent_from_file(self, name):
        filename, _file_extension = os.path.splitext(name)
        abs_filename = os.path.basename(filename)

        for size, properties in cell_types_data.iteritems():
            if cell_type in abs_filename:
                cell_id = abs_filename[properties[1]['substr_slice']: ] 
                extent = properties[0]['extent'] 
                return cell_type, cell_id, extent
   
    celltype, cell_id = type_and_id_from_filename(args.file)
    print(celltype, cell_id)

    def get_coord_tuple_from_id(self, cell_id_string):
        len_north_str = 7 # len of nrth coor, used to determ. nm. of zrs to app
        pattern = '^.*?(\d{2,6})_(\d{1,5}).*$'
        matches = re.match(pattern, cell_id_string)
        split_cellid = matches.group(1, 2)
        app_zeros = (len_north_str - len(split_cellid[0])) * '0'
        str_coords = tuple(tup + app_zeros for tup in str_tuple)
        return tuple(int(e) for e in str_coords) 

    coord_tup = get_coord_tuple_from_id(cell_id)
    print(coord_tup)

    def get_neigbouring_coords(self, grid_size, cell_extent, x_coor, y_coor):
        grid_extent = grid_size / 2
        grid_extent_meters = grid_extent * cell_extent
        grid_list = [-grid_extent_meters, grid_extent_meters + 1, cell_extent]
        return [(y_coor + u, x_coor + i) 
                for i in range(*grid_list) 
                for u in range(*grid_list)]

    def raster_bounding_box(self, list_lower_left_coords, cell_extent): ## get_bbox
        coord_sort = sort(list_lower_left_coords, key = lambda x: (x[0], x[1])
        lower_left_coord, upper_right_coord = coord_sort[0], 
                                             coord_sort[-1]
                                             + cell_extent
        return lower_left_coord, upper_right_coord

    def file_grid(self, substr_len, arbi_prefix=None, type_prefix, coord_list, extension='.tif'):
        return [arbi_prefix
                + type_prefix
                + str(i[0])[0:substr_len + 1]
                + '_'
                + str(i[1])[0:substr_len]
                + extension
                for i in coord_list]

    def subdivide(self, out_type, filename):
        cell_sizes = {'100km': 
                      [{extent : 100000}, 
                       {substr_slice : -4}],                                         
                      '10km':
                      [{extent : 10000}, 
                       {substr_slice : -6}],                                         
                      '1km' : 
                      [{extent : 1000}, 
                       {substr_slice : -8}], 
                      '500m' : 
                      [{extent : 500},
                       {substr_slice : -10}],
                      '250m' : 
                      [{extent : 250}, 
                       {substr_slice : -12}], 
                      '100m' :
                      [{extent : 100}, 
                       {substr_slice : -10}] 
                      }
        type_cell, cell_id = type_and_id_from_filename(filename)
        current_extent = cell_sizes['type_cell'][0]['extent']
        ## SKRIV DET LIGE SOM EN CLASS OK!?


        ## tilfoej extend i meter til cell sizes dic 
        
