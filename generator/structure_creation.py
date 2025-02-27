import logging
from . import constants
from .structure import Structure, Node, Connector

logger = logging.getLogger(__name__)

structure_id = 1


def pretty_print_graph_map(graph_map, tiles=False):
    import string
    symbols = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
    size = len(string.ascii_lowercase)

    if tiles:
        row = "\n"
        for g in graph_map:
            for v in g:
                if v is None:
                    row += " "
                else:
                    row += "{}".format(v[0])
            row += "\n"
        logger.info(row)

    else:
        row = "\n"
        for g in graph_map:
            for v in g:
                if v is None:
                    row += " "
                else:
                    row += "{}".format(string.ascii_lowercase[v[1] % size])
            row += "\n"
        logger.info(row)


def update_graph_map(map_data, graph_map, id, x_min, x_max, y_min, y_max):
    collisions = []
    if x_min < 0 or y_min < 0:
        raise IndexError
    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            if graph_map[x][y] is not None and graph_map[x][y][1] != id:
                # logger.info("Collision at x {}, y {}: {}".format(x,y, graph_map[x][y].structure.id))
                logger.info("Collision at x {}, y {}: {}".format(x, y, graph_map[x][y][1]))
                collisions.append([graph_map[x][y][1], x, y])

    if len(collisions) == 0:
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                if graph_map[x][y] is None:
                    tile = map_data.get(x, y)
                    graph_map[x][y] = (tile, id)

    # remove duplicates from list
    if len(collisions) > 0:
        collisions = dict((x[0], x) for x in collisions).values()

    pretty_print_graph_map(graph_map)
    return collisions


def create(map_data, points, D=5):
    graph_map = [[None for i in range(map_data.n_cols)] for i in range(map_data.n_rows)]

    structures = {}
    cluster_collisions = {}
    global structure_id

    clusters = []
    finished_clusters = []
    connecting_nodes = []
    switcher = {"r": "l", "l": "r", "u": "d", "d": "u"}
    effects = {"l": (0, -1), "d": (1, 0), "r": (0, 1), "u": (-1, 0)}

    for p in points:
        # set id of cluster in graph map
        tile = map_data.get(p[0], p[1])
        graph_map[p[0]][p[1]] = (tile, structure_id)

        # initialize an empty list to save collisions of this cluster
        cluster_collisions[structure_id] = {}
        structures[structure_id] = Structure(structure_id)
        logger.debug("Setting core point (id {}) x: {}, y: {}".format(structure_id, p[0], p[1]))
        clusters.append([structure_id, p[0], p[0], p[1], p[1], {"l": "d", "d": "r", "r": "u", "u": "l"}, "u", D])
        structure_id += 1

    pretty_print_graph_map(graph_map)

    def failed_expansion(next):
        moves[prev_move] = next
        move = prev_move
        r_min_new, r_max_new = r_min, r_max
        c_min_new, c_max_new = c_min, c_max
        clusters.append([id, r_min_new, r_max_new, c_min_new, c_max_new, moves, move, d])

    while len(clusters) > 0:
        id, r_min, r_max, c_min, c_max, moves, prev_move, d = clusters.pop(0)
        if d > D * 4:
            continue
        move = moves[prev_move]
        logger.info(
            "id: {}, r_min: {}, r_max:{}, c_min:{}, c_max:{}, move: {}".format(id, r_min, r_max, c_min, c_max, move))
        logger.info("Move list: {}".format(moves))
        # obtain the delta values for x and y
        delta_r, delta_c = effects[move]

        r_min_new = r_min + delta_r if delta_r < 0 else r_min
        r_max_new = r_max + delta_r if delta_r > 0 else r_max
        c_min_new = c_min + delta_c if delta_c < 0 else c_min
        c_max_new = c_max + delta_c if delta_c > 0 else c_max

        logger.info(
            "Tentative: r_min: {}, r_max:{}, c_min:{}, c_max:{}".format(r_min_new, r_max_new, c_min_new, c_max_new))
        try:
            collisions = update_graph_map(map_data, graph_map, id, r_min_new, r_max_new, c_min_new, c_max_new)
            if len(collisions) > 0:
                logger.info("Found collisions between when expanding structure {}".format(id))
                for other_id, r, c in collisions:
                    if other_id not in cluster_collisions[id].keys():
                        # logger.info("id: {}, other_id: {}, r: {}, c: {}".format(id, other_id, r, c))
                        other_r = r + 1 if move == "u" else r - 1 if move == "d" else r
                        other_c = c - 1 if move == "r" else c + 1 if move == "l" else c
                        cluster_collisions[id][other_id] = (r, c)
                        cluster_collisions[other_id][id] = (other_r, other_c)
                        logger.info("Expanding Structure structure {}, r {}, c {}".format(id, other_r, other_c))
                        logger.info("Collided structure {}, r {}, c {}".format(other_id, r, c))

                        connecting_nodes.append([r, c, move, id])
                        connecting_nodes.append([other_r, other_c, switcher[move], other_id])

                next_move = moves[move]
                if move == next_move:
                    logger.info("Cluster has finished expansion.")
                    finished_clusters.append([id, r_min_new, r_max_new, c_min_new, c_max_new])
                else:
                    failed_expansion(next_move)
            else:
                logger.info("No collisions found. Proceeding regular expansion...")
                clusters.append([id, r_min_new, r_max_new, c_min_new, c_max_new, moves, move, d + 1])

        except IndexError:
            logger.info("Accessing invalid index. Reverting expansion")
            next_move = moves[move]
            if move == next_move:
                logger.info("Cluster has finished expansion.")
                finished_clusters.append([id, r_min_new, r_max_new, c_min_new, c_max_new])
            else:
                failed_expansion(next_move)

    logger.info("Clusters at the end of expansions: ")
    for id, r_min, x_max, c_min, c_max in finished_clusters:
        logger.info(
            "id: {}, r_min: {}, r_max:{}, c_min:{}, c_max:{}, move: {}".format(id, r_min, x_max, c_min, c_max, move))

    logger.info("Connecting nodes: ")
    for c in connecting_nodes:
        # logger.info("Node structure_id: {}, r: {}, c: {} ".format(c.structure.id, c.r, c.c))
        logger.info("Node: {}".format(c))
        # logger.info(c.edges)

    structures = generate_structures(graph_map, connecting_nodes)

    logger.info("Generated structures: ")
    for s in structures:
        logger.info(s)

    return structures


def generate_structures(graph_map, connecting_nodes):
    structures = {}

    for r in range(len(graph_map)):
        for c in range(len(graph_map[r])):
            n = graph_map[r][c]

            if n is not None:
                if n[1] not in structures.keys():
                    structures[n[1]] = Structure(n[1])

                node = Node(r, c, n[0], "Solid" if n[0] in constants.platform_tiles else "Non-Solid", structures[n[1]])
                structures[n[1]].append_node(node)

    for r, c, direction, id in connecting_nodes:
        connector = Connector(r, c, direction, structures[id])
        structures[id].append_connector(connector)

    return list(structures.values())
