import GenericGridTools
import time
import random


class Pheromone():

    base_chance = 150
    pheromone_cap = 1000
    pheromone_increment_mult = 0.02
    pheromone_decay_rate = -50
    #a mask: 1 to use col 0 to mask (1, 0 ,0) gives only red
    def __init__(self, color_mask):
        self.color_mask = color_mask
        self.pheromone = 0.0

    def put_pheromone(self):
        increment = (self.pheromone_cap - self.pheromone) * self.pheromone_increment_mult
        self.change_pheromone(increment)

    def pheromone_decay(self, delta_time):
        self.change_pheromone(self.pheromone_decay_rate * delta_time)
        self.time_prev = time.clock()

    def change_pheromone(self, increment):
        self.pheromone += increment
        self.pheromone = min(self.pheromone_cap, max(0, self.pheromone))
        #if check to prevent wall colour from decaying


class Cell(GenericGridTools.GenericCell):

    def __init__(self, x, y):
        GenericGridTools.GenericCell.__init__(self, x, y)
        self.pheromones = {"alfa" : Pheromone((0, 0, 0)),
                          "beta" : Pheromone((0, 0, 1))}
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

    def pheromone_decay(self, type):
        delta_time = time.clock() - self.time_prev
        self.pheromones[type].pheromone_decay(delta_time)
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

    def create_grid(self):
        self.grid = [[0 for x in range(self.tile_amount)] for y in range(self.tile_amount)]
        for x in range (0, self.tile_amount):
            for y in range (0, self.tile_amount):
                new_cell = Cell(x, y)
                self.check_neighbours(new_cell, x, y)
                self.grid[x][y] = new_cell

    def decay_cell(self, n):
        n.pheromone_decay("alfa")
        n.pheromone_decay("beta")

    def update_cell_color(self, n):
        n.update_color()

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
        self.path = []
        self.found_food = False
        self.is_done = False
        self.put_type = "alfa"
        self.follow_type = "beta"

        #This is just for testing
        self.trips = 0
        self.exploration = random.uniform(0.0, 0.5)

    def __repr__(self):
        if self.current_node is not None:
            return str(self.current_node.x) + " " + str(self.current_node.y)

    def update(self):
        self.determine_move()

    def weighted_choice(self, neighbours, p_type):
        total_weight = 0.0
        cum_weights = []
        possible_moves = []
        [possible_moves.append(x) for x in neighbours if not x.closed]
        if random.random < self.exploration:
            return random.choice(possible_moves)
        else:
            for n in possible_moves:
                total_weight += n.pheromones[p_type].pheromone +Pheromone.base_chance
                cum_weights.append(total_weight)
            rnd = random.random() * total_weight
            for i, total in enumerate(cum_weights):
                if total > rnd:
                    return possible_moves[i]

    def check_goal_completed(self):
        if self.current_node.contains_food and not self.found_food:
            self.found_food = True
            self.put_type = "beta"
            self.follow_type = "alfa"

        if self.current_node.is_nest and self.found_food:
            self.found_food = False
            self.put_type = "alfa"
            self.follow_type = "beta"
            self.trips += 1

    def determine_move(self):
        if self.current_node.closed or len(self.current_node.neighbours.values()) < 1:
            self.is_done = True
        else:
            chosen_move = self.weighted_choice(self.current_node.neighbours.values(), self.follow_type)
            #This if statement is only True when user paints walls during simulation
            if chosen_move is None:
                self.is_done = True
                return

            self.prev_node = self.current_node
            self.path.append(self.prev_node)

            self.current_node.put_pheromone(self.put_type)
            self.current_node = chosen_move

            #Check if ant found food, or returned home with food
            self.check_goal_completed()

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

