from sklearn.linear_model import LinearRegression
from generator.constants import platform_tiles, enemy_tiles, powerup_tiles
from tools.render_level.render_level import parse_file
from numpy import mean
import numpy as np
from new_logs.my_loggers import logger
from glob import glob
from sklearn import preprocessing
import matplotlib.pyplot as plt
import pandas as pd

LINE_HEIGHT: [int] = 2  # for some reason height closer to 0 produces higher linearity score?


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

    gaps_count = len(gaps)
    average_gap = 0
    if not len(gaps) == 0:
        average_gap = mean(gaps)
    enemies_count = len(enemies)
    powerups_count = len(powerups)

    leniency = 0
    leniency += gaps_count * 0.5
    leniency += average_gap * 1
    leniency += enemies_count * 1
    leniency += powerups_count * -1

    logger.debug(f"gaps:{gaps}")
    logger.debug(f"enemies: {enemies}")
    logger.debug(f"powerups: {powerups}")

    logger.debug(f"[gaps count] 0.5 * {gaps_count} = {0.5 * gaps_count}")
    logger.debug(f"[average gap] 1 * {average_gap} = {average_gap}")
    logger.debug(f"[enemies count] 1 * {enemies_count} = {enemies_count}")
    logger.debug(f"[powerups count] -1 * {powerups_count} = {-powerups_count} ")

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


def get_platform_heights(max_heights: list[int]) -> list[int]:
    """
        input: array of ints representing the max height in each column
        output: list of platform heights, consecutive equal heights are considered to be one platform
        Len of this list is a number of platforms
    """

    platform_heights = []
    logger.debug(f"max heights: {max_heights}")

    for i, (height, next_height) in enumerate(zip(max_heights, max_heights[1:])):
        if height != next_height:
            platform_heights.append(height)
            logger.debug(f"platform at height {height}")
        else:
            if i == len(max_heights) - 2:
                logger.debug(f"last tile at height {next_height}")
                platform_heights.append(next_height)

    return platform_heights


def calculate_line_distance(level_data: list[str]):
    max_heights = get_platform_heights(get_max_heights(level_data))

    diff: [float] = 0 # TODO: uncomment for different approach to linearity
    for height in max_heights:
        diff += abs(height - LINE_HEIGHT)
    return diff / len(max_heights)


def calculate_linearity(level_data: list[str]):
    max_heights = get_platform_heights(get_max_heights(level_data))

    y = np.array(max_heights)
    logger.info(f"Max heights: {max_heights}")
    x = np.array(list(range(len(y)))).reshape((-1, 1))

    model = LinearRegression().fit(x, y)

    r_sqr = model.score(x, y)
    # print(f"coefficient of determination: {r_sqr}")
    # print(f"intercept: {model.intercept_}")
    # print(f"slope: {model.coef_}")

    y_predict = model.predict(x)
    logger.info(f"Predicted heights: {y_predict}")

    # print(f"predicted: {y_predict}")

    diff = 0
    for actual, predicted in zip(y, y_predict):
        diff += abs(actual - predicted)

    return diff / len(max_heights)


def plot(path: str, plot_title: str, data_frame):
    leniencies = []
    linearities = []
    for filename in glob(path, recursive=False):
        # for filename in glob("../samples/no_overlap/levels/*.txt", recursive=False):
        # for filename in glob("../maps/*.txt", recursive=False):
        logger.info("")
        logger.info("")
        logger.info(f"Analyzing {filename}")
        level = parse_file(filename)

        leniencies.append(calculate_leniency(level))
        linearities.append(calculate_linearity(level))

    normalised_leniencies = preprocessing.normalize(np.array([leniencies]), norm='max')

    normalised_linearities = preprocessing.normalize(np.array([linearities]), norm='max')

    y = normalised_leniencies[0]
    x = normalised_linearities[0]

    # print(x)
    # print(y)

    # data_frame.loc[len(data_frame)] = [path, y, x]
    data_frame['leniency'] = y
    data_frame['filename'] = 'huj'
    data_frame['linearity'] = x

    plt.plot(0, 0, 'w.')
    plt.plot(1, 1, 'w.')
    plt.plot(x, y, 'o')

    plt.xlabel(plot_title)

    plt.show()


generation_times = []
linearities = []
leniencies = []
line_distances = []
structures_used_list = []
level_lengths = []

df = pd.DataFrame(columns=['time', 'leniency', 'linearity', 'line_distance', 'structures_used', 'level_length'])


def save_data(path: str):
    df['time'] = generation_times
    df['leniency'] = leniencies
    df['linearity'] = linearities
    df['line_distance'] = line_distances
    df['structures_used'] = structures_used_list
    df['level_length'] = level_lengths

    df.to_csv(f'{path}/data_collected.csv', index=False)


if __name__ == '__main__':
    plot("../samples/overlap/levels/*.txt", "overlap", df)
 #   plot("../samples/no_overlap/levels/*.txt", "no_overlap", df)

    # save_data()
