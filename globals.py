#from maze import Maze

_maze = 'maze1'
_timespan = 100
_maxtimespan = 1000

dir_mazes = {'maze1': 'test_maze_01.txt',
            'maze2': 'test_maze_02.txt',
            'maze3': 'test_maze_03.txt'}
#testmaze = Maze( str(dir_mazes[_maze]) )


#####################

_init = [0, 0]
_distance = [0, 1, 2, 3]

#####################
_steering = ['left', 'front', 'right']
_dir_steering_to_rotation = {'left': -90, 'front': 0, 'right': 90}
_dir_steering_to_sensor_index = {'left': 0, 'front': 1, 'right': 2}

_dir_map_value = {'N': 1, 'E': 2, 'S': 4 , 'W': 8 }

_heading = ['u', 'r', 'd', 'l']
_dir_heading_to_map = {'u': 'N', 'r': 'E', 'd': 'S', 'l': 'W',
                       'up': 'N', 'right': 'E', 'down': 'S', 'left': 'W'}
_dir_int = {'u': 1, 'r': 2, 'd': 4, 'l': 8,
            'up': 1, 'right': 2, 'down': 4, 'left': 8}

_dir_heading_to_symbol = {'u': '^', 'r': '>', 'd': 'v', 'l': '<',
                          'up': '^', 'right': '>', 'down': 'v', 'left': '<'}


_dir_sensors = {'u': ['l', 'u', 'r'], 'r': ['u', 'r', 'd'],
               'd': ['r', 'd', 'l'], 'l': ['d', 'l', 'u'],
               'up': ['l', 'u', 'r'], 'right': ['u', 'r', 'd'],
               'down': ['r', 'd', 'l'], 'left': ['d', 'l', 'u']}
_dir_move = {'u': [0, 1], 'r': [1, 0], 'd': [0, -1], 'l': [-1, 0],
            'up': [0, 1], 'right': [1, 0], 'down': [0, -1], 'left': [-1, 0]}
_dir_steering_cost = {'u': 20, 'r': 20, 'd': 20, 'l': 20,
            'up': 20, 'right': 20, 'down': 20, 'left': 20}
#_dir_steering_cost_dir_cost = {'u': 1, 'r': 1, 'd': 1, 'l': 1,
#            'up': 1, 'right': 1, 'down': 1, 'left': 1}
_dir_reverse = {'u': 'd', 'r': 'l', 'd': 'u', 'l': 'r',
               'up': 'd', 'right': 'l', 'down': 'u', 'left': 'r'}