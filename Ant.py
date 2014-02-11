import GenericGridTools
import time


class Cell(GenericGridTools.GenericCell):
    def __init__(self, x, y):
        GenericGridTools.Cell.__init__(self, x, y)
        self.pheromone = 0.0


class Graph(GenericGridTools.GenericGraph):
    def __init__(self, tile_amount):
        GenericGridTools.GenericGraph.__init__(self, tile_amount)
        self.nest_node = None
        self.food_node = None


class Ant:
    def __init__(self, start_node):
        self.current_node = start_node

    def __repr__(self):
        if self.current_node is not None:
            return str(self.current_node.x) + " " + str(self.current_node.y)

    def update(self):
        self.determine_move()

    def determine_move(self):
        pass



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

