import globals
import random
import copy

from IPython.core import debugger
debug = debugger.Pdb().set_trace

class Plan(object):
    
    def __init__(self, robot, cost = 1):
        '''
        Use the initialization function to set up attributes
        '''
        
        self.robot = robot
        self.map = robot.map
        self.grid_size = len(robot.map.grid[0])
        
        self.start = robot.get_start()
        self.init = robot.location
        self.set_goal()
        
        self.is_exploring = True
        self.is_goal_reached = False
        self.is_looking_for_start = False
        
        self.cost = cost
        self.make_heuristic()
        
        self.path = []
        self.path_to_goal = [] # used for some algorithms like recursive
        self.policy = []
        self.expand = []
       
    
    
    def reset(self):
        '''
        Resets properties that are used in following runs
        '''
        
        self.start = self.robot.get_start()
        self.init = self.robot.location
        self.set_goal()
        
        self.is_exploring = False
        self.is_goal_reached = False
        self.is_looking_for_start = False
        
        self.path = []
        self.policy = []
        self.expand = []
        
     
    
    def set_goal(self, goal_type='Goal'):
        '''
        Calculate goal function for a grid
        '''
        
        if goal_type == 'Goal':
            self.goal = [self.grid_size/2 - 1, self.grid_size/2]
        elif goal_type == 'Start':
            self.goal = self.robot.start
            
    
    
    def set_goal_reached(self):
        '''
        Calculated for goal reach
        '''
        
        self.is_goal_reached = self.robot.location[0] in self.goal and self.robot.location[1] in self.goal
    
    
    
    def set_steering_by_path(self, idx = 0):
        '''
        Returns steering angle for given heading
        '''
        
        steering = globals._steering[1]
        
        if len(self.path) > 0:
            try:
                for direction in globals._steering:
                    if globals._dir_sensors[self.robot.heading][globals._dir_steering_to_sensor_index[direction]] == self.path[idx]:
                        steering = direction
            except IndexError:
                print('--- No path segmet found ---')     
        else:
            print('--- No path found ---')
                    
        return steering
    
    
    
    def check_movement(self, path_step, heading):
        '''
        Checks if we need to do a reverse movement
        '''
        if globals._dir_reverse[heading] == path_step:
            return -1
        else:
            return 1
    
    
    
    def make_heuristic(self):
        '''
        Make heuristic function for a grid
        '''
        
        self.heuristic = [[0 for row in range(self.grid_size)] 
                          for col in range(self.grid_size)]
        
        for i in range(self.grid_size):    
            for j in range(self.grid_size):
                self.heuristic[i][j] = abs(i - self.goal[0]) + abs(j - self.goal[1])
                  
                    
                    
    def random(self):
        '''
        Random search for goal
        '''
        
        x = self.init[0]
        y = self.init[1]
        
        heading_backup = copy.copy(globals._heading)
        
        steering = globals._steering[1]
        steering_heading = globals._heading[0]
        
        for i in range(len(globals._heading)):
            direction = heading_backup.pop(random.randrange(len(heading_backup)))
            heading = globals._dir_move[direction]

            # check if we can proceed 
            if self.map.is_permissible([x, y], direction):
                steering_heading = direction
                break
                
        # steering
        for direction in globals._steering:
            if globals._dir_sensors[self.robot.heading][globals._dir_steering_to_sensor_index[direction]] == steering_heading:
                steering = direction
                break
        
        # movement
        movement = self.check_movement(steering_heading, self.robot.heading)
        
        
        #steering = random.choice(_steering) 

        
        return steering, movement
    


    def recursive_search(self, init):
        '''
        Recursive search for goal
        '''
        
        action = [[-1 for col in range(self.grid_size)] for row in range(self.grid_size)]
        reverse_path = []
        
        # initialize policy or assign to plan policy to keep track
        if len(self.policy) == 0:
            policy = [[' ' for col in range(self.grid_size)] for row in range(self.grid_size)]
            policy[self.goal[0]][self.goal[1]] = 'x'
        else:
            policy = self.policy
            
        # initialize path or assign to plan path to keep track
        if len(self.path) == 0:
            path = []
        else:
            path = self.path
            
        
        goal = False
        found = True
        next_move = False
        
        x = init[0]
        y = init[1]
        
        while not goal and not next_move:
            found_heading = []
            found_resign = False
            
            # check if we are done
            if x == self.goal[0] and y == self.goal[1]:
                goal = True

            for i in range(len(globals._heading)):
                heading = globals._dir_move[globals._heading[i]]

                x2 = x
                y2 = y
                
                if  x2 >= 0 and x2 < self.grid_size and y2 >= 0 and y2 < self.grid_size:
                    
                    # check if we can proceed
                    if self.map.is_permissible([x2, y2], globals._heading[i]):
                        x2 = x + heading[0]
                        y2 = y + heading[1]
                        
                        if  x2 >= 0 and x2 < self.grid_size and y2 >= 0 and y2 < self.grid_size and self.map.is_unknown([x2, y2]):
                            action[x][y] = i
                            policy[x][y] = globals._dir_heading_to_symbol[globals._heading[i]]
                            path.append(globals._heading[action[x][y]])
                            found_heading.append(True)
                            next_move = True
                            break
                            
                        else:
                            found_heading.append(False)
                    else:
                        found_heading.append(False)
                else:
                    found_heading.append(False)
                            
            # iterate through all found headings nad check for possible path
            for i in range(len(found_heading)):
                if found_heading[i]:
                    found_resign = True
                    
            found = found_resign
            next_move = True
                            
        # if we have not found a path, go back one step
        if not found:
            last_idx = len(path) - 1
            last_path_element = path[last_idx]
            reverse_heading = globals._dir_reverse[last_path_element]
            reverse_action = globals._heading.index(reverse_heading)
            
            # set action and policy to backwards
            action[x][y] = reverse_action
            policy[x][y] = globals._dir_heading_to_symbol[reverse_heading]
            
            # remove last path item and new element
            path.pop()
            # this new path element has to be removed after steering as well
            path.append(globals._heading[action[x][y]])
            
            reverse_path = copy.copy(path)
            # remove last element (move back) from reverse_path as well
            # this reverse path will be returned and will replace normal path
            # after steering was done on normal path
            reverse_path.pop()
            
            
        # Return path, policy arrays
        return path, policy, reverse_path
            
        
        
    def recursive(self, path=False):
        '''
        Recursive main
        '''
        
        if self.is_goal_reached and len(self.path_to_goal) == 0:
            self.path_to_goal = copy.copy(self.path)
        
        if path:
            self.is_exploring = False
            
            # return optimal path and policy
            return self.path_to_goal, self.policy
        
        # assign class variables
        self.path, self.policy, reverse_path = self.recursive_search(self.init)
        
        # set steering
        if len(self.path) != 0:
            # as we do not have a path in future but in past
            # we need to past the last path element
            idx = len(self.path) - 1
            steering = self.set_steering_by_path(idx)
        
        # check for reverse movement
        # as we do not have a path in future but in past
        # we need to past the last path element
        idx = len(self.path) - 1
        last_path_element = self.path[idx]
        movement = self.check_movement(last_path_element, self.robot.heading)

        # if we move back, we replace path with replace path
        if len(reverse_path) > 0:
            self.path = copy.copy(reverse_path)

        # return steering direction and movement
        return steering, movement
        
        
        
    def astar_search(self, init, is_path):
        '''
        A* search for goal
        '''
        
        # Init arrays
        closed = [[0 for col in range(self.grid_size)] for row in range(self.grid_size)]
        closed[init[0]][init[1]] = 1
        expand = [[-1 for col in range(self.grid_size)] for row in range(self.grid_size)]
        action = [[-1 for col in range(self.grid_size)] for row in range(self.grid_size)]

        # Init parameters
        x = init[0]
        y = init[1]
        g = 0
        h = self.heuristic[x][y]
        f = g + h

        found = False
        resign = False
        count = 0
        
        # Set open on beginning of algorithm
        open = [[f, h, g, x, y]]
        
        # Loop while goal is not found or stuck
        while not found and not resign:
            
            # Goal found
            if len(open) == 0:
                resign = True
                print ("Failed as not path found")
            
            # Goal not yet found
            else:
                open.sort()
                open.reverse()
                next = open.pop()
                x = next[3]
                y = next[4]
                g = next[2]

                expand[x][y] = count
                count += 1

                # check if we are done
                if x == self.goal[0] and y == self.goal[1]:
                    found = True

                else:
                    for i in range(len(globals._heading)):
                        heading = globals._dir_move[globals._heading[i]]
                        
                        x2 = x
                        y2 = y

                        # check if we can proceed or if unknown
                        if is_path:
                            if self.map.is_permissible([x2, y2], globals._heading[i]):
                                x2 = x + heading[0]
                                y2 = y + heading[1]

                                if  x2 >= 0 and x2 < self.grid_size and y2 >= 0 and y2 < self.grid_size:
                                    if closed[x2][y2] == 0:
                                        # Steering is accounted with higher costs
                                        # to support direct movements
                                        if globals._dir_move[self.robot.heading] == heading:
                                            g2 = g + self.cost
                                        else:
                                            g2 = g + globals._dir_steering_cost[globals._heading[i]]

                                        h2 = self.heuristic[x2][y2]
                                        f2 = g2 + h2
                                        open.append([f2, h2, g2, x2, y2])
                                        closed[x2][y2] = 1
                                        action[x2][y2] = i
                        else:
                            if self.map.is_permissible([x2, y2], globals._heading[i]) or self.map.is_unknown([x2, y2]):
                                x2 = x + heading[0]
                                y2 = y + heading[1]

                                if  x2 >= 0 and x2 < self.grid_size and y2 >= 0 and y2 < self.grid_size:
                                    if closed[x2][y2] == 0:
                                        # Steering is accounted with higher costs
                                        # to support direct movements
                                        if self.robot.heading == heading:
                                            g2 = g + self.cost
                                        else:
                                            g2 = g + globals._dir_steering_cost[globals._heading[i]]

                                        h2 = self.heuristic[x2][y2]
                                        f2 = g2 + h2
                                        open.append([f2, h2, g2, x2, y2])
                                        closed[x2][y2] = 1
                                        action[x2][y2] = i
        
        
        # Set optimal policy
        policy = [[' ' for col in range(self.grid_size)] for row in range(self.grid_size)]
        x = self.goal[0]
        y = self.goal[1]
        policy[x][y] = 'x'
        
        # Set optimal path
        invpath = []
        while x != init[0] or y != init[1]:
            x2 = x - globals._dir_move[globals._heading[action[x][y]]][0]
            y2 = y - globals._dir_move[globals._heading[action[x][y]]][1]
            policy[x2][y2] = globals._dir_heading_to_symbol[globals._heading[action[x][y]]]
            invpath.append(globals._heading[action[x][y]])
            x = x2
            y = y2
            
        path = []
        for i in range(len(invpath)):
            path.append(invpath[len(invpath) - 1 - i])
            
        # Return path, policy and expand arrays
        return path, policy, expand
    
    
    
    def astar(self, path=False):
        '''
        A* main
        '''
           
        # reset plan in case of path finding (not exploring) 
        if path:
            self.reset()
            
        if self.heuristic == []:
            raise ValueError, "Heuristic must be defined to run A*"
        
        # perform a* search
        self.path, self.policy, self.expand = self.astar_search(self.init, path)
        
        # set steering
        if len(self.path) != 0:   
            steering = self.set_steering_by_path()
        
        # differentiate between path searching or next steering
        if path:
            # return optimal path and policy
            return self.path, self.policy
        else:
            # check for reverse movement
            movement = self.check_movement(self.path[0], self.robot.heading)
            
            # return steering direction and movement
            return steering, movement
    
    
    
    def dp_search(self, init):
        '''
        Dynamic Programming search for goal
        '''
        
        value = [[999 for col in range(self.grid_size)] for col in range(self.grid_size)]
        action = [[-1 for col in range(self.grid_size)] for row in range(self.grid_size)]
        
        policy = [[' ' for col in range(self.grid_size)] for row in range(self.grid_size)]
        policy[self.goal[0]][self.goal[1]] = '*'
    
        change = True
        while change:
            change = False
            
            for x in range(self.grid_size):
                for y in range(self.grid_size):

                    if x == self.goal[0] and y == self.goal[1]:
                        if value[x][y] > 0:
                            value[x][y] = 0
                            change = True

                    else:
                        for i in range(len(globals._heading)):
                            heading = globals._dir_move[globals._heading[i]]

                            x2 = x
                            y2 = y

                            # check if we can proceed 
                            if self.map.is_permissible([x2, y2], globals._heading[i]):
                                x2 = x + heading[0]
                                y2 = y + heading[1]

                                if  x2 >= 0 and x2 < self.grid_size and y2 >= 0 and y2 < self.grid_size:
                                    v2 = value[x2][y2] + self.cost
                                    
                                    if v2 < value[x][y]:
                                        change = True
                                        value[x][y] = v2
                                        action[x][y] = i
                                        policy[x][y] = globals._dir_heading_to_symbol[globals._heading[i]]

        # Set optimal policy
        x = init[0]
        y = init[1]
        
        # Set optimal path
        path = []
        while x != self.goal[0] or y != self.goal[1]:
            x2 = x + globals._dir_move[globals._heading[action[x][y]]][0]
            y2 = y + globals._dir_move[globals._heading[action[x][y]]][1]
            path.append(globals._heading[action[x][y]])
            x = x2
            y = y2
            
        return path, policy
    

    
    def dp(self, path=False):
        '''
        Dynamic Programming main
        '''
        
        # reset plan in case of path finding (not exploring) 
        if path:
            self.reset()
            
        # perform dynamic programming search
        self.path, self.policy = self.dp_search(self.init)
        
        # set steering
        if len(self.path) != 0:   
            steering = self.set_steering_by_path()
        
        # differentiate between path searching or next steering
        if path:
            # return optimal path and policy
            return self.path, self.policy
        else:
            movement = self.check_movement(self.path[0], self.robot.heading)
            # check for reverse movement
            
            # return steering direction and movement
            return steering, movement