# import substructure_manipulation
import logging
import copy
from . import constants
from .level import Level

logger = logging.getLogger(__name__)


class Connector:
    def __init__(self, r, c, direction, structure=None):
        self.r = r
        self.c = c
        self.direction = direction
        self.combined = None
        self.combinable = []
        self.structure = structure

    def __repr__(self):
        return "(Connector sub_id:{}, ({},{}) combinable: {})\n".format(self.sub_id, self.r, self.c, self.combinable)


class Node:
    def __init__(self, r, c, tile="-", type="Non-Solid", structure=None):
        self.r = r
        self.c = c
        self.tile = tile
        self.type = type
        self.structure = structure
        self.edges = []

    def __repr__(self):
        return "Node({},{} {})".format(self.r, self.c, self.tile)


class Structure:

    def __init__(self, structure_id):
        self.id = structure_id
        self.sub_id = 0  # sub_id for connectors
        self.nodes = []
        self.connecting = []
        self.enemies = 0

    def n_connecting(self):
        return len(self.connecting)

    def n_enemies(self):
        return self.enemies

    def append_node(self, n):
        self.nodes.append(n)
        if n.tile in constants.enemy_tiles:
            self.enemies += 1

    def append_connector(self, c):
        c.sub_id = self.sub_id
        self.sub_id += 1
        self.connecting.append(c)

    def get_connector(self, sub_id):
        logger.info("Trying to get sub_id: {}".format(sub_id))
        for c in self.connecting:
            logger.info("Checking: {}".format(c.sub_id))
            if c.sub_id == sub_id:
                return c

    def relativize_coordinates(self):
        """Shift all nodes so the left-most node has column==0"""
        if len(self.nodes) + len(self.connecting) < 1:
            return
        smallest_c = (self.nodes + self.connecting)[0].c
        for node in self.nodes + self.connecting:
            if node.c < smallest_c:
                smallest_c = node.c
        for node in self.nodes + self.connecting:
            node.c = node.c - smallest_c

    def available_substitutions(self):
        substitutions = []
        for n in self.connecting:
            if n.combined is None:
                for s_id, n2 in n.combinable:
                    substitutions.append((self, n, s_id, n2))
        return substitutions

    def __repr__(self):
        return f"StructureID: {self.id}"
        # return "ID: {} \n Connecting Nodes: {} ".format(self.id, self.connecting)
        # return "ID: {}\n Nodes: {}\n Connecting Nodes: {}".format(self.id, self.nodes, self.connecting)

    def matrix_representation(self):
        generated = Level(" ")

        for node in self.nodes:
            generated.set(node.r, node.c, node.tile)
        directions = {"r": ">", "l": "<", "u": "^", "d": "v"}
        for connector in self.connecting:
            generated.set(connector.r, connector.c, directions[connector.direction])

        return generated.matrix_representation()

    def level_representation(self, filler=True):
        # 1: find the highest column values
        highest_column = 0
        for node in self.nodes + self.connecting:
            if node.c > highest_column:
                highest_column = node.c

        # 2: create a matrix with [16][n_columns]
        base_tile = "-" if filler else " "
        level = [[" " for i in range(highest_column + 1)] for j in range(16)]

        # 3: fill the matrix with * where * is a
        # placeholder image (maybe an empty 17x16 png)

        # 4: iterate over all nodes and place tiles in
        # the appropriate locations in the matrix
        directions = {"r": ">", "l": "<", "u": "^", "d": "v"}
        for node in self.nodes:
            level[node.r][node.c] = node.tile
        for node in self.connecting:
            level[node.r][node.c] = directions[node.direction]

        # 5: return the matrix, to be used in render_level
        return level

    def pretty_print(self, filler=True):

        level = self.level_representation(filler)
        full_string = ""

        for row in level:
            row_str = ""
            for tile in row:
                row_str += tile
            full_string += row_str + "\n"

        return full_string

    def save_as_level(self, level_filename="output.txt"):
        generated = Level()

        for n in self.nodes:
            # print("Inserting node: {},{}".format(n.r, n.c))
            generated.set(n.r, n.c, n.tile)

        generated.save_level(level_filename)
