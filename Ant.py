import GenericGridTools
import time
import operator
import random



class Cell(GenericGridTools.GenericCell):
    #This needs heavy tweaking
    pheromone_decay_rate = -0.001

    def __init__(self, x, y):
        GenericGridTools.GenericCell.__init__(self, x, y)
        self.pheromone = float(0.0)
        self.contains_ant = False
        self.contains_food = False

    def ant_enter(self, pheromone_increase):
        self.change_pheromone(pheromone_increase)
        if not self.contains_ant:
            self.contains_ant = True

    def ant_exit(self):
        if self.contains_ant:
            self.contains_ant = False

    def pheromone_decay(self):
        self.change_pheromone(self.pheromone_decay_rate)

    def change_pheromone(self, increment):
        self.pheromone += increment
        self.pheromone = max(0, self.pheromone)
        self.change_color(increment)

    def change_color(self, increment):
        increment *= -1
        col_multiplier = 10
        self.color = (self.color[0], self.color[1]+(increment*col_multiplier), self.color[2]+(increment*col_multiplier))
        self.color = (self.color[0], min(255, max(0, self.color[1])), min(255, max(0, self.color[2])))

    def add_food(self):
        self.contains_food = True


class Graph(GenericGridTools.GenericGraph):
    def __init__(self, tile_amount):
        GenericGridTools.GenericGraph.__init__(self, tile_amount)
        self.nest_node = None
        self.food_node = None
        self.create_grid()

    def create_grid(self):
        self.grid = [[0 for x in range(self.tile_amount)] for y in range(self.tile_amount)]
        for x in range (0, self.tile_amount):
            for y in range (0, self.tile_amount):
                new_cell = Cell(x, y)
                self.check_neighbours(new_cell, x, y)
                self.grid[x][y] = new_cell

    def decay_all_cells(self):
        for x in range(0, self.tile_amount):
            for y in range(0, self.tile_amount):
                self.grid[x][y].pheromone_decay()

    def update(self):
        self.decay_all_cells()


class Ant:

    def __init__(self, start_node):
        self.current_node = start_node
        self.current_node.ant_enter(0)
        self.prev_node = None
        self.path = []
        self.pheromone_increment = 0
        self.found_food = False
        self.is_done = False

    def __repr__(self):
        if self.current_node is not None:
            return str(self.current_node.x) + " " + str(self.current_node.y)

    def update(self):
        self.determine_move()

    def determine_move(self):
        possible_moves = []
        if not self.found_food:
            #This choice needs to be weighted by pheromone levels, current version is just to test.
            for n in self.current_node.neighbours.values():
                if not n.closed and n is not self.prev_node:
                    possible_moves.append(n)
            self.prev_node = self.current_node
            self.current_node = random.choice(possible_moves)
            self.path.append(self.prev_node)

            #Check if new cell has food
            if self.current_node.contains_food:
                self.found_food = True
                self.pheromone_increment = 1
        else:
            if len(self.path) > 0:
                self.prev_node = self.current_node
                self.current_node = self.path[len(self.path)-1]
                self.path.pop()
            else:
                self.is_done = True

        self.prev_node.ant_exit()
        self.current_node.ant_enter(self.pheromone_increment)

class AntController:
    def __init__(self, ants_amount, ants_per_tick):
        self.ants_amount = ants_amount
        self.ants_per_tick = ants_per_tick
        self.nest = None
        self.ant_list = []
        self.time_prev = time.clock()
        self.ant_timer = 1.0
        self.ant_timer_original = self.ant_timer

    #This can create more ants than specified but it's not really important
    def create_ants(self):
        if self.nest is not None:
            for x in range(0, self.ants_per_tick):
                a = Ant(self.nest)
                self.ant_list.append(a)
            self.ants_amount -= self.ants_per_tick
            print ("Created " +str(self.ants_per_tick) +" ants")

    def update_timer(self):
        current_time = time.clock()
        self.ant_timer -= current_time - self.time_prev
        self.time_prev = current_time

    def reset_timer(self):
        self.ant_timer = self.ant_timer_original

    def update_ants(self):
        for a in self.ant_list:
            a.update()

    def remove_dead_ants(self):
        ants_to_remove = []
        for ant in self.ant_list:
            if ant.is_done:
                ants_to_remove.append(ant)
        if len(ants_to_remove) > 0:
            [self.ant_list.remove(ant) for ant in ants_to_remove]

    def update(self):
        self.update_timer()
        if self.ant_timer < 0 < self.ants_amount:
            self.create_ants()
            self.reset_timer()
        self.update_ants()
        self.remove_dead_ants()

