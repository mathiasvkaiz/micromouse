import globals
import numpy as np

from IPython.core import debugger
debug = debugger.Pdb().set_trace

class Map(object):
    def __init__(self, map_dim):
        '''
        Use the initialization function to set up attributes
        '''

        self.map_dim = map_dim
        self.grid = [[-1 for col in range(map_dim)] for row in range(map_dim)]
        self.visited = [[-1 for col in range(map_dim)] for row in range(map_dim)]
        self.moved = [[' ' for col in range(map_dim)] for row in range(map_dim)]
        
        
        
    def reset(self):
        '''
        Resets properties that are used in following runs
        '''
        
        self.visited = [[-1 for col in range(self.map_dim)] for row in range(self.map_dim)]
        self.moved = [[' ' for col in range(self.map_dim)] for row in range(self.map_dim)]
        
        
        
    def is_permissible(self, cell, direction):
        """
        Returns a boolean designating whether or not a cell is passable in the
        given direction. Cell is input as a list. Directions may be
        input as single letter 'u', 'r', 'd', 'l', or complete words 'up', 
        'right', 'down', 'left'.
        """
        
        if self.is_unknown(cell):
            return False
        
        try:
            return (self.grid[cell[0]][cell[1]] & globals._dir_int[direction] != 0)
        except:
            print cell, direction, ' is a wall!'
           
        
        
    def is_unknown(self, cell):
        '''
        Checks if a given cell is unknown (not yet explored/visited)
        '''
        
        return self.grid[cell[0]][cell[1]] == -1
        
        
        
    def expand(self, location, heading, sensors):
        '''
        Expand function that documents explored cells
        '''
        
        value = 0
        # TODO refactor
        # check sensor steering
        for direction in globals._steering:
            if sensors[globals._dir_steering_to_sensor_index[direction]] > 0:
                i = globals._dir_map_value[globals._dir_heading_to_map[globals._dir_sensors[heading][globals._dir_steering_to_sensor_index[direction]]]]
                value += i
                
        # map reverse if not at starting position
        # TODO: refactor fo better way
        if (location != globals._init):
            value += globals._dir_map_value[globals._dir_heading_to_map[globals._dir_reverse[heading]]]
        
        # set value
        if self.grid[location[0]][location[1]] == -1:
            self.grid[location[0]][location[1]] = value
            
            
            
    def check_coverage(self):
        '''
        Calcluates the exploration coverage of the map
        '''
        unique, counts = np.unique(self.visited, return_counts=True)
        dir_coverage = dict(zip(unique, counts))
        total = np.prod(np.array(self.visited).shape)
        
        if float(dir_coverage[1]) / float(total) >= 0.7:
            return True
        else:
            return False 