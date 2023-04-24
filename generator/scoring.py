import logging
from .level import Level
from . import constants

logger = logging.getLogger(__name__)


def get_intervals(number, inter, skip=0):
    """Given an integer and a value for interval, return a list of
  tuples containing intervals within the 0-number range.
  e.g. 15 --> [(0,4),(5,9), (10,14)]
  """
    intervals = []
    inter_start = skip

    for i in range(number + 1):
        if i - inter_start == inter:
            intervals.append((inter_start, i - 1))
            inter_start = i

    if i - inter_start > 0:
        intervals.append((inter_start, i - 1))

    return intervals


def get_enemy_density(level, start_col=0, end_col=0):
    end_col = level.n_cols if (end_col == 0) else end_col
    enemies = 0
    for c in range(start_col, end_col + 1):
        for r in range(level.n_rows):
            if level.get(r, c) in constants.enemy_tiles:
                enemies += 1
    return enemies


def create_level(structures):
    level = Level()
    for structure in structures:
        for node in structure.nodes:
            level.set(node.r, node.c, node.tile)
    return level


def get_density_score(structures, d=3, l=14):
    logger.info("Calculating density...")
    level = create_level(structures)

    # get intervals representing scenes, eg. 3-17, 18-34n
    intervals = get_intervals(level.n_cols, l, 3)
    logger.debug("Number of columns: {}".format(level.n_cols))
    logger.debug("Scenes in the level: \n{}".format(intervals))

    enemy_denisities = []
    for start_col, end_col in intervals:
        enemy_denisities.append(get_enemy_density(level, start_col, end_col))

    logger.debug("Enemies on each interval: \n{}".format(enemy_denisities))

    # different calculation
    enemy_denisities = [(abs(density - d)) for density in enemy_denisities]
    score = sum(enemy_denisities)
    logger.debug("Score: {}".format(score))

#    logger.debug("Enemies found on each interval: \n{}".format(enemy_denisities))

    return score


def get_increasing_density_score(structures, d=2, l=14):
    logger.debug("Calculating density...")
    level = create_level(structures)

    # get intervals representing scenes, eg. 3-17, 18-34n
    intervals = get_intervals(level.n_cols, l, 3)
    logger.debug("Number of columns: {}".format(level.n_cols))
    logger.debug("Scenes in the level: \n{}".format(intervals))

    enemy_densities = []
    for start_col, end_col in intervals:
        enemy_densities.append(get_enemy_density(level, start_col, end_col))

    logger.debug("Enemies on each interval: \n{}".format(enemy_densities))

    # different calculation
    enemy_densities = [(abs(density - (d * i))) for i, density in zip(range(len(enemy_densities)), enemy_densities)]
    logger.debug("After processing: \n{}".format(enemy_densities))
    score = sum(enemy_densities)
    logger.debug("Score: {}".format(score))

#    logger.debug("Enemies found on each interval: \n{}".format(enemy_densities))

    return score


def get_platforms_count(level):
    platform_nodes = 0
    for node in level.nodes:
        if node.tile == "X":
            platform_nodes += 1
    return platform_nodes


def get_enemies_count(level):
    enemy_nodes = 0
    for n in level.nodes:
        if n.tile in constants.enemy_tiles:
            enemy_nodes += 1
    return enemy_nodes
