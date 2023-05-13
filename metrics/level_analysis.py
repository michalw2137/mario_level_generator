from sklearn.linear_model import LinearRegression
from generator.constants import platform_tiles, enemy_tiles, powerup_tiles
from tools.render_level.render_level import parse_file
from numpy import mean
import numpy as np
from new_logs.my_loggers import logger
from glob import glob
from sklearn import preprocessing
import matplotlib.pyplot as plt


def get_gaps(level_data: list[str]) -> list[int]:
    """
    input: 2d array of characters representing the level
    output: list of gaps, each number represents length in blocks.
    Len of this list is a number of gaps in the level
    """
    last_row = level_data[-1]

    gap_lengths = []
    gap_length = 1

    for block, next_block in zip(last_row, last_row[1:]):
        if block not in platform_tiles:
            if next_block not in platform_tiles:
                gap_length += 1
            else:
                gap_lengths.append(gap_length)
                gap_length = 1
    return gap_lengths


def get_tiles(level_data: list[str], searched_tiles: list[str]) -> list[str]:
    """
    input: 2d array of characters representing the level
    output: list of characters found in level that belong to filter list
    """
    powerups_found = []

    for row in level_data:
        for tile in row:
            if tile in searched_tiles:
                powerups_found.append(tile)
    return powerups_found


def calculate_leniency(level_data: list[str]) -> float:
    gaps = get_gaps(level_data)
    enemies = get_tiles(level_data, enemy_tiles)
    powerups = get_tiles(level_data, powerup_tiles)

    logger.debug(f"gaps:{gaps}")
    logger.debug(f"enemies: {enemies}")
    logger.debug(f"powerups: {powerups}")

    gaps_count = len(gaps)
    average_gap = 0
    if not len(gaps) == 0:
        average_gap = mean(gaps)
    enemies_count = len(enemies)
    powerups_count = len(powerups)

    leniency = 0
    leniency += gaps_count * -0.5
    leniency += average_gap * -1
    leniency += enemies_count * -1
    leniency += powerups_count * 1

    logger.info(f"leniency = {leniency}")

    return leniency


def get_max_heights(level_data: list[str]) -> list[int]:
    max_heights = [0] * len(level_data[0])
    level_height = len(level_data)
    # print(f"max heights: {max_heights}")

    # print(f"level height: {level_height}")
    for y, row in enumerate(level_data):
        for x, block in enumerate(row):
            if max_heights[x] != 0:
                continue
            if block in platform_tiles:
                max_heights[x] = level_height - y
    # print(f"max heights: {max_heights}")

    return max_heights


def calculate_linearity(max_heights: list[int]):
    y = np.array(max_heights)
    x = np.array(list(range(len(y)))).reshape((-1, 1))

    model = LinearRegression().fit(x, y)

    r_sqr = model.score(x, y)
    # print(f"coefficient of determination: {r_sqr}")
    # print(f"intercept: {model.intercept_}")
    # print(f"slope: {model.coef_}")

    y_predict = model.predict(x)
    # print(f"predicted: {y_predict}")

    diff = 0
    for actual, predicted in zip(y, y_predict):
        diff += abs(actual - predicted)

    return diff


if __name__ == '__main__':
    leniencies = []
    linearities = []
    # for filename in glob("../samples/overlap/levels/*.txt", recursive=False):
    for filename in glob("../samples/no_overlap/levels/*.txt", recursive=False):
        # for filename in glob("../maps/*.txt", recursive=False):
        logger.info(f"Analyzing {filename}")
        level = parse_file(filename)

        leniencies.append(calculate_leniency(level))
        linearities.append(calculate_linearity(get_max_heights(level)))

    normalised_leniencies = preprocessing.normalize(np.array([leniencies]), norm='max')

    normalised_linearities = preprocessing.normalize(np.array([linearities]), norm='max')

    y = normalised_leniencies[0]
    x = normalised_linearities[0]

    print(x)
    print(y)

    plt.plot(x, y, 'o')

    plt.show()
