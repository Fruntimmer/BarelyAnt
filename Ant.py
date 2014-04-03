import GenericGridTools
import time
import random


class Pheromone():

    pheromone_cap = 10
    pheromone_increment_mult = 0.2
    pheromone_decay_rate = -.3

    def __init__(self):
        self.pheromone = 0.0

    def put_pheromone(self):
        increment = (self.pheromone_cap - self.pheromone) * self.pheromone_increment_mult
        self.change_pheromone(increment)

    def pheromone_decay(self, delta_time):
        self.change_pheromone((self.pheromone * self.pheromone_decay_rate) * delta_time)
        #self.change_pheromone(self.pheromone_decay_rate * delta_time)

    def change_pheromone(self, increment):
        self.pheromone += increment
        self.pheromone = min(self.pheromone_cap, max(0, self.pheromone))


class Cell(GenericGridTools.GenericCell):

    def __init__(self, x, y):
        GenericGridTools.GenericCell.__init__(self, x, y)
        self.pheromones = {"alfa" : Pheromone(),
                           "beta" : Pheromone()}
        self.contains_ant = False
        self.contains_food = False
        self.is_nest = False
        self.time_prev = time.clock()

    def ant_enter(self):
        self.contains_ant = True

    def ant_exit(self):
        self.contains_ant = False

    def put_pheromone(self, type):
        self.pheromones[type].put_pheromone()

    def pheromone_decay(self):
        delta_time = time.clock() - self.time_prev
        self.pheromones["alfa"].pheromone_decay(delta_time)
        self.pheromones["beta"].pheromone_decay(delta_time)
        self.time_prev = time.clock()

    def update_color(self):
        new_col = (self.pheromones["alfa"].pheromone/Pheromone.pheromone_cap,
                   0, self.pheromones["beta"].pheromone/Pheromone.pheromone_cap)

        self.color = (255-new_col[0]*255, 255-new_col[1]*255, 255-new_col[2]*255)

    def add_food(self):
        self.contains_food = True


class Graph(GenericGridTools.GenericGraph):
    def __init__(self, tile_amount):
        GenericGridTools.GenericGraph.__init__(self, tile_amount)
        self.nest_node = None
        self.food_node = None
        self.create_grid()
        self.decay_ticker = 0

    def create_grid(self):
        self.grid = [[0 for x in range(self.tile_amount)] for y in range(self.tile_amount)]
        for x in range (0, self.tile_amount):
            for y in range (0, self.tile_amount):
                new_cell = Cell(x, y)
                self.check_neighbours(new_cell, x, y)
                self.grid[x][y] = new_cell

    def decay_cell(self, n):
        n.pheromone_decay()

    def update_cell_color(self, n):
        n.update_color()

    # def update(self):
    #     if self.decay_ticker > 9:
    #         for x in range(0, self.tile_amount):
    #             for y in range(0, self.tile_amount):
    #                 self.decay_cell(self.grid[x][y])
    #                 self.update_cell_color(self.grid[x][y])
    #     self.decay_ticker += 1
    def update(self):
        for x in range(0, self.tile_amount):
            for y in range(0, self.tile_amount):
                self.decay_cell(self.grid[x][y])
                self.update_cell_color(self.grid[x][y])


class Ant:
    def __init__(self, start_node):
        self.current_node = start_node
        self.current_node.ant_enter()
        self.prev_node = None
        self.found_food = False
        self.is_done = False
        self.put_type = "alfa"
        self.follow_type = "beta"
        self.origin = start_node
        #Ant randomness
        self.exploration = random.uniform(0.0, 0.3)
        self.best_bias = random.uniform(0.75-self.exploration, 0.95)

        #This is just for testing
        self.steps_taken = 0
        self.start_max_step = 100
        self.max_steps = self.start_max_step
        self.trips = 0
        self.short_mem = []

    def __repr__(self):
        if self.current_node is not None:
            return str(self.current_node.x) + " " + str(self.current_node.y)

    def add_mem(self, cell):
        if len(self.short_mem) > 8:
            self.short_mem.pop(0)
        self.short_mem.append(cell)

    def weighted_choice(self, neighbours, p_type):
        possible_moves = []
        for n in neighbours:
            if n.is_nest and self.found_food:
                return n
            elif n.contains_food and not self.found_food:
                return n
            elif n not in self.short_mem and not n.closed:
                possible_moves.append(n)
        if len(possible_moves) == 0:
            [possible_moves.append(x) for x in neighbours if not x.closed]
        # if random.random() < self.exploration:
        #     return random.choice(possible_moves)
        # else:
        possible_moves.sort(key=lambda p: p.pheromones[p_type].pheromone, reverse=True)
        for n in possible_moves:
            if n.pheromones[p_type].pheromone == 0:
                break
            elif random.random() < self.best_bias:
                return n
        return random.choice(possible_moves)

    def check_goal_completed(self):
        if self.current_node.contains_food and not self.found_food:
            self.found_food = True
            self.put_type = "beta"
            self.follow_type = "alfa"
            self.origin = self.current_node
            #self.max_steps = self.start_max_step + int(((self.max_steps - self.start_max_step) * 0.3))
            #self.max_steps = 100
            self.steps_taken = 0
            self.short_mem = []

        elif self.current_node.is_nest and self.found_food:
            self.found_food = False
            self.put_type = "alfa"
            self.follow_type = "beta"
            self.origin = self.current_node
            self.steps_taken = 0
            self.max_steps = self.start_max_step + int(((self.max_steps - self.start_max_step) * 0.3))
            self.short_mem = []
            self.trips += 1
            print("That was trip number " +str(self.trips))

    def determine_move(self):
        self.steps_taken += 1
        chosen_move = None
        if self.current_node.closed or len(self.current_node.neighbours.values()) < 1:
            self.is_done = True
            print("I die. This should only happen if you are drawing walls")
        elif self.steps_taken > self.max_steps:
            #Ant has failed and its max range is increased
            self.steps_taken = 0
            self.max_steps *= 1.3
            chosen_move = self.origin
        else:
            chosen_move = self.weighted_choice(self.current_node.neighbours.values(), self.follow_type)
            #This if statement is only True when user paints walls during simulation
            if chosen_move is None:
                self.is_done = True
                return

        self.prev_node = self.current_node
        self.current_node.put_pheromone(self.put_type)
        self.current_node = chosen_move

        #Check if ant found food, or returned home with food
        self.check_goal_completed()

        self.prev_node.ant_exit()
        self.add_mem(self.prev_node)
        self.current_node.ant_enter()

    def update(self):
        self.determine_move()


class AntController:

    def __init__(self, max_ants, ants_per_tick):
        self.total_ants = 0
        self.max_ants = max_ants
        self.ants_per_tick = ants_per_tick
        self.nest = None
        self.ant_list = []
        self.time_prev = time.clock()
        self.ant_timer = 1
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

    def remove_done_ants(self):
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
        self.remove_done_ants()

