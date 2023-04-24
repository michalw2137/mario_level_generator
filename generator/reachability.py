import logging
import math
import operator

logger = logging.getLogger(__name__)


def compute_reachability(node1, node2):
    def inside_triangle(x1, y1, x2, y2, x3, y3, x, y):

        def area(x1, y1, x2, y2, x3, y3):
            return abs((x1 * (y2 - y3) + x2 * (y3 - y1)
                        + x3 * (y1 - y2)) / 2.0)

        area1 = area(x1, y1, x2, y2, x3, y3)
        area2 = area(x, y, x2, y2, x3, y3)
        area3 = area(x1, y1, x, y, x3, y3)
        area4 = area(x1, y1, x2, y2, x, y)
        return abs(area2 + area3 + area4 - area1) <= 0.001

    def inside_rectangle(left_x, right_x, bottom_y, top_y, x, y):
        if left_x <= x <= right_x and bottom_y >= y >= top_y:
            return True
        else:
            return False

    logger.debug("Calculating Rectangle and Triangles from node {}...".format(node1))
    h_dist = 3
    v_dist = 4

    rect_c_min = 0 if node1.c - h_dist < 0 else node1.c - h_dist
    rect_c_max = node1.c + h_dist
    rect_r_min = 0 if node1.r - v_dist < 0 else node1.r - v_dist
    rect_r_max = 15 if node1.r + v_dist > 15 else node1.r + v_dist

    logger.debug("c_min: {}, c_max: {}".format(rect_c_min, rect_c_max))
    logger.debug("r_min: {}, r_max: {}".format(rect_r_min, rect_r_max))

    t1_p1_c = rect_c_min
    t1_p1_r = rect_r_min

    t1_p2_c = rect_c_min
    t1_p2_r = 15

    # loose approximation
    t1_p3_c = rect_c_min - (15 - rect_r_min) / 2
    if t1_p3_c < 0: t1_p3_c = 0
    t1_p3_r = 15

    logger.debug(
        "t1 p1: ({},{}), p2: ({},{}), p3: ({},{}),".format(t1_p1_r, t1_p1_c, t1_p2_r, t1_p2_c, t1_p3_r, t1_p3_c))

    t2_p1_c = rect_c_max
    t2_p1_r = rect_r_min

    t2_p2_c = rect_c_max
    t2_p2_r = 15

    # loose approximation
    t2_p3_c = rect_c_max + int((15 - rect_r_min) / 2)
    t2_p3_r = 15

    # logger.info("Difference x: {}, difference y: {}".format(difference_x, difference_y))
    # angle = math.degrees(math.atan2(difference_x, difference_y))
    # logger.info("atan: {}".format(angle))

    logger.info(
        "t2 p1: ({},{}), p2: ({},{}), p3: ({},{}),".format(t2_p1_r, t2_p1_c, t2_p2_r, t2_p2_c, t2_p3_r, t2_p3_c))

    triang1 = inside_triangle(t1_p1_c, t1_p1_r, t1_p2_c, t1_p2_r, t1_p3_c, t1_p3_r, node2.c, node2.r)
    logger.info("Checking if inside triangle 1: {}".format(triang1))

    triang2 = inside_triangle(t2_p1_c, t2_p1_r, t2_p2_c, t2_p2_r, t2_p3_c, t2_p3_r, node2.c, node2.r)
    logger.info("Checking if inside triangle 2: {}".format(triang2))

    rect = inside_rectangle(rect_c_min, rect_c_max, rect_r_max, rect_r_min, node2.c, node2.r)
    logger.info("Checking if inside rectangle: {}".format(rect))

    return triang1 or triang2 or rect


def get_distances(s1, s2):
    """
  Returns the distances between all solid tiles and other solid/non-solid tiles
  """

    def dist(node1, node2):
        x = pow(node2.r - node1.r, 2)
        y = pow(node2.c - node1.c, 2)
        return math.sqrt(x + y)

    s1_solids = []
    s2_solids = []
    s2_nonsolids = []

    for node in s1.nodes:
        if node.type == "Solid":
            s1_solids.append(node)
    for node in s2.nodes:
        if node.type == "Solid":
            s2_solids.append(node)
        elif node.type == "Non-Solid":
            s2_nonsolids.append(node)

    logger.info("s1 solids: {}".format(s1_solids))
    logger.info("s2 solids: {}".format(s2_solids))

    distances = []
    for n1 in s1_solids:
        for n2 in s2_solids + s2_nonsolids:
            d = dist(n1, n2)
            distances.append((d, n1, n2))

    distances.sort(key=operator.itemgetter(0))

    return distances


def is_reachable(structure1, structure2, dist=4.5):
    logger.info("Calculating Reachability...")
    logger.info("S1: \n{}".format(structure1.pretty_print()))
    logger.info("S2: \n{}".format(structure2.pretty_print()))

    distances = get_distances(structure1, structure2)

    for d, n1, n2 in distances:
        logger.info("dist: {}, n1: {}, n2: {}".format(d, n1, n2))

        if compute_reachability(n1, n2):
            logger.info("Reachable!")
            return True
        else:
            logger.info("Not reachable!")
    return False
