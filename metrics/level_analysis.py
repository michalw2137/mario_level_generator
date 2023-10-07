import logging
import os

from sklearn.linear_model import LinearRegression
from generator.constants import platform_tiles, enemy_tiles, powerup_tiles
from tools.render_level.render_level import parse_file
from numpy import mean
import numpy as np
from sklearn import preprocessing
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# Set the Pandas display options to show all columns
pd.set_option('display.max_columns', None)
# Set the Pandas display options to disable scientific notation
pd.set_option('display.float_format', '{:.2f}'.format)
# Set the Pandas display options to exclude count
pd.set_option('display.show_dimensions', False)

logging.basicConfig(filename="output/log.log",
                    level=logging.DEBUG,
                    filemode='w')

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

    logging.debug(f"gaps:{gaps}")
    logging.debug(f"enemies: {enemies}")
    logging.debug(f"powerups: {powerups}")

    logging.debug(f"[gaps count] 0.5 * {gaps_count} = {0.5 * gaps_count}")
    logging.debug(f"[average gap] 1 * {average_gap} = {average_gap}")
    logging.debug(f"[enemies count] 1 * {enemies_count} = {enemies_count}")
    logging.debug(f"[powerups count] -1 * {powerups_count} = {-powerups_count} ")

    logging.info(f"leniency = {leniency}")

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
    logging.debug(f"max heights: {max_heights}")

    for i, (height, next_height) in enumerate(zip(max_heights, max_heights[1:])):
        if height != next_height:
            platform_heights.append(height)
            logging.debug(f"platform at height {height}")
        else:
            if i == len(max_heights) - 2:
                logging.debug(f"last tile at height {next_height}")
                platform_heights.append(next_height)

    return platform_heights


def calculate_line_distance(level_data: list[str]):
    max_heights = get_platform_heights(get_max_heights(level_data))

    diff: [float] = 0  # TODO: uncomment for different approach to linearity
    for height in max_heights:
        diff += abs(height - LINE_HEIGHT)
    return diff / len(max_heights)


def calculate_linearity(level_data: list[str]):
    max_heights = get_platform_heights(get_max_heights(level_data))

    y = np.array(max_heights)
    logging.info(f"Max heights: {max_heights}")
    x = np.array(list(range(len(y)))).reshape((-1, 1))

    model = LinearRegression().fit(x, y)

    r_sqr = model.score(x, y)
    # print(f"coefficient of determination: {r_sqr}")
    # print(f"intercept: {model.intercept_}")
    # print(f"slope: {model.coef_}")

    y_predict = model.predict(x)
    logging.info(f"Predicted heights: {y_predict}")

    # print(f"predicted: {y_predict}")

    diff = 0
    for actual, predicted in zip(y, y_predict):
        diff += abs(actual - predicted)

    return diff / len(max_heights)


def plot(path: str, plot_title: str, data_frame):
    leniencies = []
    linearities = []

    print(os.listdir(path))
    for filename in os.listdir(path):
        # for filename in glob("../samples/no_overlap/levels/*.txt", recursive=False):
        # for filename in glob("../maps/*.txt", recursive=False):

        logging.info("")
        logging.info("")
        logging.info(f"Analyzing {filename}")
        level = parse_file(os.path.join(path, filename))

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


structure_ids = []
generation_times = []
linearities = []
leniencies = []
line_distances = []
structures_used_list = []
structures_count_list = []
backtrackings = []
level_lengths = []


df = pd.DataFrame(
    columns=['time', 'leniency', 'linearity', 'line_distance', 'structures_used', 'structures_count', 'backtrackings', 'level_length'])


structures_frame = pd.DataFrame(
    columns=['id', 'leniency', 'linearity', 'line_distance'])


def save_data(path: str):
    df['time'] = generation_times
    df['leniency'] = leniencies
    df['linearity'] = linearities
    df['line_distance'] = line_distances
    df['structures_used'] = structures_used_list
    df['structures_count'] = structures_count_list
    df['backtrackings'] = backtrackings
    df['level_length'] = level_lengths

    df.to_csv(f'{path}/data_collected.csv', index=False)


def save_structures_data(path: str):
    structures_frame['id'] = structure_ids
    structures_frame['leniency'] = leniencies
    structures_frame['linearity'] = linearities
    structures_frame['line_distance'] = line_distances

    structures_frame.to_csv(path, index=False)
    linearities.clear()
    leniencies.clear()
    line_distances.clear()

def analyze_structures(path: Path):
    for filename in os.listdir(path):
        if ".txt" not in filename or "struct_stats" in filename:
            # print(f"skipping {filename}")
            continue

        structure = parse_file(os.path.join(path, filename))

        structure_ids.append(filename[2:-4])
        leniencies.append(calculate_leniency(structure))
        linearities.append(calculate_linearity(structure))
        line_distances.append(calculate_line_distance(structure))


if __name__ == '__main__':
    analyze_structures(Path("../samples/level1_remix/structures"))
    save_structures_data(f'./output/data_collected.csv')
# plot("../samples/level1_remix/structures/", "overlap", df)
#   plot("../samples/no_overlap/levels/*.txt", "no_overlap", df)
# save_data()
