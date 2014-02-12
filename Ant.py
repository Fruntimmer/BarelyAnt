import GenericGridTools
import time
import operator
import random



class Cell(GenericGridTools.GenericCell):
    pheromone_decay_rate = 0.1

    def __init__(self, x, y):
        GenericGridTools.GenericCell.__init__(self, x, y)
        self.pheromone = float(0.0)
        self.contains_ant = False

    def ant_enter(self, pheromone_increase):
        self.change_pheromone(pheromone_increase)
        if not self.contains_ant:
            self.contains_ant = True

    def ant_exit(self):
        if self.contains_ant:
            self.contains_ant = False

    def pheromone_decay(self):
        self.change_pheromone(self, self.pheromone_decay_rate)

    def change_pheromone(self, increment):
        self.pheromone += increment
        #Do something about color


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


class Ant:
    pheromone_increase = 1

    def __init__(self, start_node):
        self.current_node = start_node
        self.current_node.ant_enter(0)
        self.prev_node = None

    def __repr__(self):
        if self.current_node is not None:
            return str(self.current_node.x) + " " + str(self.current_node.y)

    def update(self):
        self.determine_move()

    def determine_move(self):
        possible_moves = []
        for n in self.current_node.neighbours.values():
            if not n.closed and n is not self.prev_node:
                possible_moves.append(n)
        self.prev_node = self.current_node
        self.current_node = random.choice(possible_moves)
        self.prev_node.ant_exit()
        self.current_node.ant_enter(self.pheromone_increase)


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


    def update(self):
        self.update_timer()
        if self.ant_timer < 0 < self.ants_amount:
            self.create_ants()
            self.reset_timer()
        self.update_ants()

#ac = AntController(100, 10, GridTools.Cell(5, 6))
