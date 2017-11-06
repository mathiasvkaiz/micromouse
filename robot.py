import globals

from map import Map
from plan import Plan
from maze import Maze

import sys
import numpy as np
import os
import copy

from IPython.core import debugger
debug = debugger.Pdb().set_trace

class Robot(object):
    def __init__(self, map_dim):
        '''
        Use the initialization function to set up attributes that your robot
        will use to learn and navigate the maze. Some initial attributes are
        provided based on common information, including the size of the maze
        the robot is placed in.
        '''
        self.start = [0, 0]
        self.location = self.get_start()
        self.heading = 'up'
        
        self.map = Map(map_dim)
        self.plan = Plan(self)
        
        self.timespan = globals._timespan
        self.timestep = 0
        self.explored_timestep = 0
        self.overall_tiestep = 0
        self.max_timestep = globals._maxtimespan

        # different explore algorithms
        try:
          	self.explorer_name = os.environ['EXPLORER']
        except:
          	self.explorer_name = 'astar'

      	if self.explorer_name=='random':
    		self.explorer = self.plan.random
    	elif self.explorer_name=='recursive':
    		self.explorer = self.plan.recursive
    	elif self.explorer_name=='astar':
    		self.explorer = self.plan.astar
    	else:
    		self.explorer = self.plan.astar



      	# different search path algorithms for best path
        try:
            self.search_name = os.environ['SEARCH']
        except:
           	self.search_name = 'astar'

       	if self.search_name=='recursive':
        	self.search = self.plan.recursive
        elif self.search_name=='dp':
        	self.search = self.plan.dp
        elif self.search_name=='astar':
        	self.search = self.plan.astar
        else:
        	self.search = self.plan.astar
        
        
        
    def reset(self):
        '''
        Resets properties that are used in following runs
        '''
        
        self.location = self.get_start()
        self.heading = 'up'
        self.explored_timestep = self.timestep
        self.timestep = 0
            
    
    
    def set_heading(self, steering):
        '''
        Sets heading based on given steering
        '''
        
        self.heading = globals._dir_sensors[self.heading][globals._dir_steering_to_sensor_index[steering]]
        
     
    
    def get_start(self):
        '''
        Getter for start cell
        '''
        return copy.copy(self.start)
    
    

    def next_move(self, sensors):
        '''
        Use this function to determine the next move the robot should make,
        based on the input from the sensors after its previous move. Sensor
        inputs are a list of three distances from the robot's left, front, and
        right-facing sensors, in that order.

        Outputs should be a tuple of two values. The first value indicates
        robot rotation (if any), as a number: 0 for no rotation, +90 for a
        90-degree rotation clockwise, and -90 for a 90-degree rotation
        counterclockwise. Other values will result in no rotation. The second
        value indicates robot movement, and the robot will attempt to move the
        number of indicated squares: a positive number indicates forwards
        movement, while a negative number indicates backwards movement. The
        robot may move a maximum of three units per turn. Any excess movement
        is ignored.

        If the robot wants to end a run (e.g. during the first training run in
        the maze) then returing the tuple ('Reset', 'Reset') will indicate to
        the tester to end the run and return the robot to the start.
        '''

        rotation = 0
        movement = 0
        	
        
        # for report purposes
        old_location = [self.location[0], self.location[1]]
        
        # map surrounding
        self.map.expand(self.location, self.heading, sensors)
        
        # set visited
        self.map.visited[self.location[0]][self.location[1]] = 1
        
        # check if we have a 70% coverage of the map or time is elapsed
        if (self.map.check_coverage() and self.plan.is_goal_reached) or self.timestep == self.max_timestep - self.timespan:
            # Reset everything
            self.reset()

            

            self.plan.path, self.plan.policy = self.search(True) #self.plan.astar(True)
#             self.plan.path, self.plan.policy = self.plan.dp(True)
#             self.plan.path, self.plan.policy = self.plan.recursive(True)
            
            # Debug Reports
            # print ('MOVED by ' + self.explorer_name) 
            # print (np.rot90(self.map.moved))
            
            # print ('') 
            # print ('') 
            
            #print ('POLICY by ' + self.search_name) 
            #print (np.rot90(self.plan.policy))

            #print ('') 

            print ('PATH by ' + self.search_name) 
            print(self.plan.path)
            #print ('\n'.join(str(p) for p in self.plan.path))

            print ('') 

            print ('PATH length: ' + str(len(self.plan.path)))
            print ('Coverage: ' + str(self.map.coverage))

            print ('') 
            
        
            # Reset map
            self.map.reset()
    
            # Reset run
            return ('Reset', 'Reset')    
        
        # check for exploration mode
        if self.plan.is_exploring:
            # check for goal
            self.plan.set_goal_reached()
            
            if self.plan.is_goal_reached:
#                 print('######################## GOAL REACHED #########################')
                # explore back to start in case it is not already doing so
                if not self.plan.is_looking_for_start:
                    self.plan.set_goal('Start')
                    self.plan.is_looking_for_start = True
                else:
                    self.plan.set_goal()
                    self.plan.is_looking_for_start = False

            steering, movement = self.explorer() #self.plan.astar()
#             steering, movement = self.plan.random()
#             steering, movement = self.plan.recursive()

    
        else:
            # walk by given path
            steering, movement = self.plan.set_steering_by_path(self.timestep), 1
            
            self.overall_timestep = self.timestep + self.explored_timestep
#             if self.overall_timestep == self.max_timestep:
#                 print (np.rot90(self.map.moved)) 
        
        
        # perform rotation and set new heading
        rotation = globals._dir_steering_to_rotation[steering]
        self.set_heading(steering)
        
        # perform movement
        if abs(movement) > 3:
            print "Movement limited to three squares in a turn."
        movement_steps = max(min(int(movement), 3), -3) # fix to range [-3, 3]
        while movement_steps:
            if movement_steps > 0:
                if movement_steps <= sensors[globals._dir_steering_to_sensor_index[steering]] and self.map.is_permissible(self.location, self.heading):
                    # map movement
                    self.map.moved[self.location[0]][self.location[1]] = globals._dir_heading_to_symbol[self.heading]

                    # perform move
                    self.location[0] += globals._dir_move[self.heading][0]
                    self.location[1] += globals._dir_move[self.heading][1]

                    self.map.moved[self.location[0]][self.location[1]] = "*"
                    movement_steps -= 1
                else:
                    print "Movement stopped by wall."
                    movement_steps = 0
            else:
                rev_heading = globals._dir_reverse[self.heading]
                if self.map.is_permissible(self.location, rev_heading):
                    # map movement
                    self.map.moved[self.location[0]][self.location[1]] = globals._dir_heading_to_symbol[rev_heading]

                    # perform move
                    self.location[0] += globals._dir_move[rev_heading][0]
                    self.location[1] += globals._dir_move[rev_heading][1]

                    self.map.moved[self.location[0]][self.location[1]] = "*"
                    movement_steps += 1
                else:
                    print "Movement stopped by wall."
                    movement_steps = 0
               
        # Debug Report
#         print '{} [{:>2d},{:>2d},{:>2d}] {:>3d} => {}, {:>2d} steps = {}'.format(
#             old_location,
#             sensors[0], sensors[1], sensors[2],
#             rotation,
#             self.heading,
#             movement,
#             self.location)
        
        # increase time
        self.timestep += 1
        
        # return actions
        return rotation, movement