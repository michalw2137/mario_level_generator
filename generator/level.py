import math


class Level:

    def __init__(self, filler="-"):
        self.map_data = []
        self.n_rows = 16
        self.n_cols = 1
        self.filler = filler

        for r in range(self.n_rows):  # * self.n_cols):
            self.map_data.append(filler)

    def append(self, value):
        self.map_data.append(value)
        self.n_cols = math.ceil(len(self.map_data) / self.n_rows)

    def get(self, x, y):
        if x > self.n_rows or y > self.n_cols:
            raise "Accessing invalid index"
        index = self.n_rows * y + x
        return self.map_data[index]

    def set(self, x, y, value):
        # print("Adding x {}, y {}".format(x, y))
        if x > self.n_rows or x < 0 or y < 0:
            # raise "Accessing invalid index"
            return
        # print("Current number of columns: {}, total: {}".format(self.n_cols, len(self.map_data)))

        while len(self.map_data) - 1 < self.n_rows * y + x:
            self.append(self.filler)

        while len(self.map_data) % 16 != 0:
            self.append(self.filler)

        # print("After appending: {}, total: {}".format(self.n_cols, len(self.map_data)))

        index = self.n_rows * y + x
        # print("index: {}".format(index))
        self.map_data[index] = value

    def apply_structure(self, s):
        for n in s.nodes:
            x = n.r
            y = n.c
            self.set(x, y, n.tile)

    def pretty_print(self):
        full_string = ""
        for i in range(self.n_rows):
            row = ""
            for j in range(self.n_cols):
                tile = self.get(i, j)
                row += str(tile)
            full_string += row + "\n"
            # print(row)
        return full_string

    def matrix_representation(self):
        level = []
        for i in range(self.n_rows):
            level.append([])
            for j in range(self.n_cols):
                level[-1].append(self.get(i, j))
        return level

    def save_level(self, level_filename="output.txt"):
        output_file = open(level_filename, "w")
        for r in range(self.n_rows):
            string = ""
            for c in range(self.n_cols):
                tile = self.get(r, c)
                string += str(tile)
            print(string, sep='', file=output_file)
        output_file.close()
