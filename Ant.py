import GenericGridTools
import time
import operator
import random



class Cell(GenericGridTools.GenericCell):
    #This needs heavy tweaking. Is measured in decay/second
    pheromone_cap = 200
    base_chance = 30
    pheromone_decay_rate = base_chance*-0.13
    pheromone_increment = base_chance*0.15

    def __init__(self, x, y):
        GenericGridTools.GenericCell.__init__(self, x, y)
        self.pheromone = float(0.0)
        self.contains_ant = False
        self.contains_food = False
        self.time_prev = time.clock()

    def ant_enter(self):
            self.contains_ant = True

    def ant_exit(self):
            self.contains_ant = False
    def put_pheromone(self):
        self.change_pheromone(self.pheromone_increment)

    def pheromone_decay(self):
        delta_time = time.clock() - self.time_prev
        self.change_pheromone(self.pheromone_decay_rate * delta_time)
        self.time_prev = time.clock()

    def change_pheromone(self, increment):
        self.pheromone += increment
        self.pheromone = min(self.pheromone_cap, max(0, self.pheromone))

        #if check to prevent wall colour from decaying
        if self.pheromone > 0:
            self.change_color(increment)

    def change_color(self, increment):
        #increment *= -1
        #col_multiplier = 20
        self.color = (self.color[0], 255-(self.pheromone/self.pheromone_cap)*255, 255-(self.pheromone/self.pheromone_cap)*255)
        #self.color = (self.color[0], min(255, max(0, self.color[1])), min(255, max(0, self.color[2])))

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
        self.current_node.ant_enter()
        self.prev_node = None
        self.path = []
        self.found_food = False
        self.is_done = False

    def __repr__(self):
        if self.current_node is not None:
            return str(self.current_node.x) + " " + str(self.current_node.y)

    def update(self):
        self.determine_move()

    def weighted_choice(self, neighbours):
        p_sum = 0.0
        possible_moves = []
        choices = []
        cumsum = 0.0
        #This is important. Closely related to pheromone increment and decay

        for n in neighbours:
            if not n.closed and n is not self.prev_node:
                possible_moves.append(n)
                p_sum += n.pheromone+n.base_chance
        if p_sum > 0:
            possible_moves.sort(key=lambda x: x.pheromone, reverse=True)
            for n in possible_moves:
                cumsum += n.pheromone+n.base_chance
                choices.append((cumsum/p_sum, n))
            rnd = random.random()

            for c in choices:
                if c[0] > rnd:
                    return c[1]
        #This only happens if user is painting walls
        return None

    def determine_move(self):
        if self.current_node.closed or len(self.current_node.neighbours.values()) < 1:
            self.is_done = True
        else:
            if not self.found_food:
                #This choice needs to be weighted by pheromone levels, current version is just to test.
                chosen_move = self.weighted_choice(self.current_node.neighbours.values())
                #This only happens if user is painting walls
                if chosen_move is None:
                    self.is_done = True
                    return

                self.prev_node = self.current_node
                self.path.append(self.prev_node)
                self.current_node = chosen_move

                #Check if new cell has food
                if self.current_node.contains_food:
                    self.found_food = True
            else:
                if len(self.path) > 0:
                    self.prev_node = self.current_node
                    self.current_node = self.path.pop()
                    self.current_node.put_pheromone()

                else:
                    self.found_food = False

            self.prev_node.ant_exit()
            self.current_node.ant_enter()

class AntController:

    def __init__(self, max_ants, ants_per_tick):
        self.total_ants = 0
        self.max_ants = max_ants
        self.ants_per_tick = ants_per_tick
        self.nest = None
        self.ant_list = []
        self.time_prev = time.clock()
        self.ant_timer = 0.5
        self.ant_timer_original = self.ant_timer

    #This can create more ants than specified but it's not really important
    def create_ants(self):
        if self.nest is not None and self.total_ants < self.max_ants:
            for x in range(0, self.ants_per_tick):
                a = Ant(self.nest)
                self.ant_list.append(a)
            self.total_ants += self.ants_per_tick

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
        if self.ant_timer < 0:
            self.create_ants()
            self.reset_timer()
        self.update_ants()
        self.remove_dead_ants()

