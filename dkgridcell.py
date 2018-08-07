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
                      [{'extent' : 100000}, 
                       {'substr_slice' : -4}, 
                       {'coord_slice' : -5}], 
                      '10km':
                      [{'extent' : 10000}, 
                       {'substr_slice' : -6}, 
                       {'coord_slice' : -4}], 
                      '1km' : 
                      [{'extent' : 1000}, 
                       {'substr_slice' : -8}, 
                       {'coord_slice' : -3}], 
                      '500m' : 
                      [{'extent' : 500},
                       {'substr_slice' : -10},
                       {'coord_slice' : -2}], 
                      '250m' : 
                      [{'extent' : 250}, 
                       {'substr_slice' : -12}, 
                       {'coord_slice' : -1}], 
                      '100m' :
                      [{'extent' : 100}, 
                       {'substr_slice' : -10},
                       {'coord_slice' : -2}] 
                      }
 
    def __init__(self, file_name):
        self.filename, self.abs_filename, self.abs_path = self.get_filemeta(file_name)    
        self.cell_type, self.cell_id, self.extent = self.type_id_extent_from_file(self.abs_filename)
        self.ll_coord = self.get_coord_tuple_from_id(self.cell_id)
        self.neigh_coords = None
        self.bbox_ll, self.bbox_ur = None, None
        self.neigh_files = None

    def get_filemeta(self, name):
        filename, _file_extension = os.path.splitext(name)
        abs_filename = os.path.basename(filename)
        abs_path = os.path.abspath(os.path.dirname(name))
        return filename, abs_filename, abs_path

    def type_id_extent_from_file(self, abs_filename):
        for cell_type, properties in self.cell_types_data.iteritems():
            if cell_type in abs_filename:
                cell_id = abs_filename[properties[1]['substr_slice']: ] 
                extent = properties[0]['extent'] 
                return cell_type, cell_id, extent
   
    def get_coord_tuple_from_id(self, cell_id_string):
        len_north_str = 7 # len of nrth coor, used to determ. nm. of zrs to app
        pattern = '.*?(\d{2,6})_(\d{1,5}).*$'
        # pattern = '.*?(\d+.?m).?(\d{2,6})_(\d{1,5}).*$' doesnt work w. 1st gp
        matches = re.match(pattern, cell_id_string)
        split_cellid = matches.group(1, 2)
        app_zeros = (len_north_str - len(split_cellid[0])) * '0'
        str_coords = tuple(tup + app_zeros for tup in split_cellid)
        return tuple(int(e) for e in str_coords) 

    def get_neigbouring_files(self, grid_size, prefix):
        x_coord, y_coord = self.ll_coord
        grid_extent = grid_size / 2
        grid_extent_meters = grid_extent * self.extent
        grid_list = [-grid_extent_meters, grid_extent_meters + 1, self.extent]
        self.neigh_coords = [(y_coord + u, x_coord + i) 
                            for i in range(*grid_list)
                            for u in range(*grid_list)]
        self.neigh_files = self.file_grid(self.neigh_coords, 
                                          self.cell_types_data[self.cell_type][2]['coord_slice'], 
                                          self.cell_type, prefix)
        return self.neigh_files

    def raster_bounding_box(self): 
        coord_sort = sorted(self.neigh_coords, key = lambda x: (x[0], x[1]))
        self.bbox_ll = coord_sort[0]
        self.bbox_ur = tuple(e + self.extent for e in coord_sort[-1])
        return self.bbox_ll, self.bbox_ur

    def file_grid(self, coord_list, substr_len, type_prefix, arbi_prefix='',
                  extension='.tif'):
        return [arbi_prefix
                + type_prefix
                + '_'
                + str(i[1])[0:substr_len]
                + '_'
                + str(i[0])[0:substr_len]
                + extension
                for i in coord_list]

    def subdivide(self, out_type):
        ll_coord = self.ll_coord
        current_extent = self.extent
        new_extent = self.cell_types_data[out_type][0]['extent']
        sub_ll = [(llx, lly) 
                  for llx in range(ll_coord[0], ll_coord[0] 
                                   + current_extent, new_extent)
                  for lly in range(ll_coord[1], ll_coord[1]
                                   + current_extent, new_extent)]
        return self.file_grid(sub_ll,
                              self.cell_types_data[out_type][2]['coord_slice'],
                              type_prefix=out_type)

    def pathify_file(self, path, file_list):
        pathified = ' '.join([os.path.join(path, f) for f in file_list]) 
        return pathified    

        
