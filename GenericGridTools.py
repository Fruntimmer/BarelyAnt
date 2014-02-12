

class GenericCell:
    sel_color = (255, 0, 0)

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.neighbours = {}
        self.closed = False
        self.parent = None

        #Vis variables
        self.color = (255, 255, 255)
        self.default_color = self.color

    def add_parent(self, node):
        self.parent = node

    def add_neighbour(self, nCell, dir1, dir2):
        if nCell not in self.neighbours:
            self.neighbours[dir1] = nCell
            nCell.neighbours[dir2] = self

    def remove_neighbour(self, neighbour):
        for key, value in self.neighbours.items():
            if neighbour == value:
                del self.neighbours[key]

    def display_neighbours(self):
        for cell in self.neighbours.values():
            cell.color = self.sel_color

    def hide_neighbours(self):
        for cell in self.neighbours.values():
            cell.color = self.default_color

    def open_node(self, grid):
        self.closed = False
        grid.check_neighbours(self, self.x, self.y, True)
        self.color = self.default_color

    def close_node(self):
        self.closed = True
        self.color = (155, 155, 155)
        for node in self.neighbours.values():
            node.remove_neighbour(self)
        self.neighbours = {}


class GenericGraph:
    def __init__(self, tile_amount):
        self.tile_amount = tile_amount
        #self.create_grid()

    def create_grid(self):
        self.grid = [[0 for x in range(self.tile_amount)] for y in range(self.tile_amount)]
        for x in range (0, self.tile_amount):
            for y in range (0, self.tile_amount):
                new_cell = GenericCell(x, y)
                self.check_neighbours(new_cell, x, y)
                self.grid[x][y] = new_cell

    def check_neighbours(self, node, x, y, all_dir=False):
        a = 1
        if y > 0 and self.is_valid_neighbour(x, y-a):
            node.add_neighbour(self.grid[x][y-a], "n", "s")

        if x > 0:
            if self.is_valid_neighbour(x-a, y):
                node.add_neighbour(self.grid[x-a][y], "w", "e")

            if y > 0 and self.is_valid_neighbour(x-a, y-a):
                node.add_neighbour(self.grid[x-a][y-a], "nw", "se")

            if y < self.tile_amount-1 and self.is_valid_neighbour(x-a, y+a):
                node.add_neighbour(self.grid[x-a][y+a], "sw", "ne")

        if all_dir:
            self.rev_check_neighbours(node, x, y)

    def rev_check_neighbours(self, node, x, y):
        a = -1

        if y < self.tile_amount-1 and self.is_valid_neighbour(x, y-a):
            node.add_neighbour(self.grid[x][y-a], "s", "n")

        if x < self.tile_amount-1:
            if self.is_valid_neighbour(x-a,y):
                node.add_neighbour(self.grid[x-a][y], "e", "w")
            if y < self.tile_amount-1 and self.is_valid_neighbour(x-a, y-a):
                node.add_neighbour(self.grid[x-a][y-a], "se", "nw")
            if y > 0 and self.is_valid_neighbour(x-a, y+a):
                node.add_neighbour(self.grid[x-a][y+a], "ne", "sw")

    def is_valid_neighbour(self, x, y):
        if self.grid[x][y] is not None and not self.grid[x][y].closed:
            return True
        else:
            return False


class GenericPath:
    def __init__(self, path):
        self.path = path