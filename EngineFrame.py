import pygame
import Ant
import time


class GraphEngine:
    background_color = (155, 155, 155)
    #current_selection = None
    #drag_node = None
    #active_mode = None

    def __init__(self, graph, width, tile_amount):
        self.width = width
        self.height = width
        #self.graph = graph
        self.tile_size = int(width/tile_amount)
        self.border = max(1, int(self.tile_size/15))
        self.screen = pygame.display.set_mode((self.width, self.height))

    def display_all_cells(self, graph):
        for x in range(0, graph.tile_amount):
            for y in range(0, graph.tile_amount):
                self.display_cell(graph.grid[x][y], self.tile_size, self.border)

    def display_cell(self, node, tile_size, border):
        color = node.color
        if node.contains_ant:
            border *=5
            color = (20, 20, 20)
        pygame.draw.rect(self.screen, color, [node.x*tile_size, node.y*tile_size, tile_size-border, tile_size-border])

    #def display_all_ants(self, ant_list):
        #for ant in ant_list:
            #display_cell(ant.current_node, self.tile_size)


    def update(self, graph):
        self.screen.fill(self.background_color)
        self.display_all_cells(graph)
        pygame.display.flip()


class GlobalController:
    def __init__(self, tile_amount, window_size, total_ants, ants_per_tick):
        self.graph = Ant.Graph(tile_amount)
        self.engine = GraphEngine(self.graph, window_size, self.graph.tile_amount)
        self.ant_controller = Ant.AntController(total_ants, ants_per_tick)
        self.active_mode = None

    def get_grid_mouse_pos(self, tile_size):
        (mouseX, mouseY) = pygame.mouse.get_pos()
        (x, y) = (int(mouseX/tile_size), int(mouseY/tile_size)) #mousepos on tilegrid
        return x, y

    def drag(self, node, grid, color,  x, y):
        if node is not None:
            node.color = node.default_color
        node = grid[x][y]
        node.color = color
        return node

    def left_click(self, grid, x, y):
        #Determins what your click will do
        active_mode = None
        if self.graph.nest_node is None:
            self.graph.nest_node = grid[x][y]
            self.graph.nest_node.color = (50, 255, 50)
        elif self.graph.food_node is None:
            if(grid[x][y] is not self.graph.nest_node):
                grid[x][y].add_food()
                self.graph.food_node = grid[x][y]
                self.graph.food_node.color = (255, 50, 50)

        elif grid[x][y] == self.graph.nest_node:
            active_mode = "dragStart"
            self.drag_node = self.graph.nest_node
        elif grid[x][y] == self.graph.food_node:
            active_mode = "dragGoal"
            self.drag_node = self.graph.food_node
        elif not grid[x][y].closed:
            active_mode = "paintWall"
        elif grid[x][y].closed:
            active_mode = "paintOpen"
        return active_mode

    def right_click(self, current_selection, grid, x, y):
        #Displays the neighbours of right clicked squares
        if current_selection is not None:
            current_selection.hide_neighbours()
        current_selection = grid[x][y]
        current_selection.display_neighbours()
        return current_selection

    def input_listen(self, run_ant, running):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                key = pygame.key.get_pressed()
                if key[pygame.K_RETURN]:
                    if self.graph.food_node is not None and self.graph.nest_node is not None:
                        self.initialize_ant_controller()
                        run_ant = True
                    else:
                        print "Missing nest or food"
            if event.type == pygame.MOUSEBUTTONDOWN:
                (b1, b2, b3) = pygame.mouse.get_pressed()
                (x, y) = self.get_grid_mouse_pos(self.engine.tile_size)

                if b1:
                    self.active_mode = self.left_click(self.graph.grid, x, y)

                if b3:
                    self.current_selection = self.right_click(self.current_selection, self.graph.grid, x, y)

            if event.type == pygame.MOUSEBUTTONUP:
                (b1, b2, b3) = pygame.mouse.get_pressed()
                #This makes it stop painting/dragging and dragging when you release mb1
                if not b1:
                    self.active_mode = None
        return run_ant, running

    def execute_active_mode(self):
        (x, y) = self.get_grid_mouse_pos(self.engine.tile_size)
        if self.active_mode == "paintWall":
            if not self.graph.grid[x][y].closed:
                self.graph.grid[x][y].close_node()
        elif self.active_mode == "paintOpen":
            if self.graph.grid[x][y].closed is True:
                self.graph.grid[x][y].open_node(self.graph)
        #Drag start/goal could be same method/mode, just the color thing needs to be adjusted.
        elif self.active_mode == "dragStart":
            self.graph.nest_node = self.drag(self.graph.nest_node, self.graph.grid, (59, 255, 50), x, y)
        elif self.active_mode == "dragGoal":
            self.graph.food_node = self.drag(self.graph.food_node, self.graph.grid, (255, 50, 50), x, y)

    def initialize_ant_controller(self):
        self.ant_controller.nest = self.graph.nest_node

    def main(self):
        run_ant = False
        running = True
        while running:
            #Checks for m+kb input
            run_ant, running = self.input_listen(run_ant, running)
            #performs actions depending on what active_mode is set to
            if self.active_mode is not None:
                self.execute_active_mode()

            self.engine.update(self.graph)
            if run_ant:
                self.ant_controller.update()
                #Graph only updates the pheromone decay of its cells so we dont need it unless ants are active
                self.graph.update()
                #time.sleep(1)

tile_amount = 50
window_size = 800
total_ants = 100
ants_per_tick = 10

gc = GlobalController(tile_amount, window_size, total_ants, ants_per_tick)
gc.main()

