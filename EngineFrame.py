import pygame
import Ant


class GraphEngine:
    background_color = (155, 155, 155)
    current_selection = None
    drag_node = None
    active_mode = None

    def __init__(self, graph, width, height):
        self.width = width
        self.height = height
        self.graph = graph
        self.tile_size = int(width/graph.tile_amount)
        self.border = max(1, int(self.tile_size/15))
        self.screen = pygame.display.set_mode((width, height))

    def display_cell(self, node, tile_size, border):
        pygame.draw.rect(self.screen, node.color, (node.x*tile_size, node.y*tile_size, tile_size-border, tile_size-border))

    def update(self):
        self.screen.fill(self.background_color)

        for x in range(0, self.graph.tile_amount):
            for y in range(0, self.graph.tile_amount):
                self.display_cell(self.graph.grid[x][y], self.tile_size, self.border)
        pygame.display.flip()


class GlobalController:
    def __init__(self):
        self.graph = Ant.Graph(50)
        self.engine = GraphEngine(self.graph, 800, 800)
        self.ant_controller = Ant.AntController(100,10)
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
        active_mode = None
        if self.graph.nest_node is None:
            self.graph.nest_node = grid[x][y]
            self.graph.nest_node.color = (50, 255, 50)
        elif self.graph.food_node is None:
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
        if current_selection is not None:
            current_selection.hide_neighbours()
        current_selection = grid[x][y]
        current_selection.display_neighbours()
        return current_selection

    def initialize_ant_controller(self):
        self.ant_controller.nest = self.graph.nest_node

    def main(self):
        run_ant = False
        running = True
        while(running):
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
                    #This makes it stop painting and dragging when you release mb1
                    if not b1:
                        self.active_mode = None

            if self.active_mode is not None:
                (x, y) = self.get_grid_mouse_pos(self.engine.tile_size)
                if self.active_mode == "paintWall":
                    if not self.graph.grid[x][y].closed:
                        self.graph.grid[x][y].close_node()
                elif self.active_mode == "paintOpen":
                    if self.graph.grid[x][y].closed is True:
                        self.graph.grid[x][y].open_node(self.graph)
                elif self.active_mode == "dragStart":
                    self.graph.nest_node = self.drag(self.graph.nest_node, self.graph.grid, (59, 255, 50), x, y)
                elif self.active_mode == "dragGoal":
                    self.graph.food_node = self.drag(self.graph.food_node, self.graph.grid, (255, 50, 50), x, y)

            self.engine.update()
            if run_ant:
                    self.ant_controller.update()

gc = GlobalController()
gc.main()

