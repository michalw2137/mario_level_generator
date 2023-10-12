import logging
import logging.handlers
import optparse
import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

import numpy as np

from generator import level_generation
from generator import structure_identification
from generator import structure_matching
from helper import io
from metrics.level_analysis import generation_times, leniencies, calculate_leniency, linearities, calculate_linearity, \
    save_data, structures_used_list, level_lengths, line_distances, calculate_line_distance, backtrackings, \
    analyze_structures, save_structures_data, structures_count_list, used_structures_list
from tools.render_level.render_level import render_structure

# uncomment for truncated file
# filehandler = log.log.TruncatedFileHandler("output/log.log", "w", 9000000)
# logging.basicConfig(
# format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#    level=logging.DEBUG, handlers=[filehandler])

logging.basicConfig(filename="output/log.log",
                    level=logging.INFO,
                    filemode='w')


def parse_args(args):
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-l', action="store", type="string",
                      dest="mapfile",
                      help="Path/name of the level file",
                      default="maps/lvl-1.txt")
    parser.add_option('-o', action="store", type="int",
                      dest="output_number",
                      help="Number of level to be generated",
                      default=10)
    parser.add_option('-n', action="store", type="int",
                      dest="n",
                      help="Number of structures to be selected",
                      default=35)
    parser.add_option('-d', action="store", type="int",
                      dest="d",
                      help="Minimum radius of structures",
                      default=4)
    parser.add_option('-s', action="store", type="int",
                      dest="s",
                      help="Extended radius of structures based on similarity",
                      default=8)
    parser.add_option('-m', action="store", type="int",
                      dest="min_structures",
                      help="Minimum number of structures for a level",
                      default=35)
    parser.add_option('-g', action="store", type="string",
                      dest="generate",
                      help="Generate or not levels based on selected structures",
                      default="True")
    parser.add_option('-r', action="store", type="string",
                      dest="render",
                      help="Render or not levels as png files",
                      default="False")
    (opt, args) = parser.parse_args()
    return opt, args


def get_level_paths(opt):
    levels = []
    if "txt" in opt.mapfile:
        print(f"txt parameter defined ({opt.mapfile})")
        levels.append([opt.mapfile, opt.n, opt.d])
    else:
        file_names = os.listdir(opt.mapfile)
        file_paths = ["{}{}".format(opt.mapfile, x) for x in file_names]
        print(f"txt parameter not defined, file paths: {file_paths}")
        for file in file_paths:
            if "DS_Store" in file:
                continue
            levels.append([file, opt.n, opt.d])
    return levels


def load_structures(path):
    structures = []
    g_s = None
    g_f = None

    for file in os.listdir(path):
        if "." not in file:
            if file == "g_s":
                g_s = io.load("{}/{}".format(path, file))
            elif file == "g_f":
                g_f = io.load("{}/{}".format(path, file))
            else:
                structure = io.load("{}/{}".format(path, file))
                structures.append(structure)
    return g_s, g_f, structures


def save_structures(g_s, g_f, structures, folder):
    for s in structures:
        io.save(s, "{}/s_{}".format(folder, s.id))
        render_structure(s.matrix_representation(),
                         "{}/s_{}.png".format(folder, s.id))
        s.save_as_level(f"{folder}/s_{s.id}.txt")

    io.save(g_s, "{}/g_s".format(folder))
    render_structure(g_s.matrix_representation(),
                     "{}/g_s.png".format(folder))

    io.save(g_f, "{}/g_f".format(folder))
    render_structure(g_f.matrix_representation(),
                     "{}/g_f.png".format(folder))

    output_file = open("{}/struct_stats.txt".format(folder), "w")

    # for s in structures:
    #     substitutions = s.available_substitutions()
    #     print("{}, {}, {}".format(s.id, len(s.connecting),
    #                               len(substitutions)),
    #           file=output_file)
    #     ##
    #     print(s, "Substitutions: ", s.connecting)
    #     print()
    #     print("substitutions.txt: ", substitutions)
    #     print("----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    #     print("----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    output_file.close()


def extract_structures(data):
    """
  Returns g_s, g_f, and a list of structures given levels in data.
  data: list of tuples of (path, n, d)
  """
    # Randomnly select 'n' points each level in data
    # with a minimum of d size each
    structures = []
    for level, n, d in data:
        level_structures = structure_identification.extract_structures(level, n, d)
        structures.extend(level_structures)

    # Instiate the base starting and finishing structures
    g_s, g_f = level_generation.instantiate_base_level(len(structures) + 1)
    # save_structures(g_s, g_f, structures)
    return g_s, g_f, structures


def get_subset(structures, n=0.1):
    """
  Given a list of structures, return a list with n% of them.
  The probability of selection of a given structure is
  proportional to the amount of connectors and enemies.
  p(s) = 2*c + e
  """
    dimensions = ["n_connecting", "n_enemies"]
    bins = {}

    for str in structures:
        str_dimensions = []
        for d in dimensions:
            str_dimensions.append(getattr(str, d)())
        # logging.info("Attrs of str {}: {}".format(str.id, str_dimensions))

        key = tuple(str_dimensions)
        if key not in bins.keys():
            bins[key] = []
        bins[key].append(str)

    struct_list = []
    probab_list = []
    for con, en in bins.keys():
        probability = con * 2 + en
        for str in bins[(con, en)]:
            struct_list.append(str)
            probab_list.append(probability)

    probab_list = [x / sum(probab_list) for x in probab_list]

    n_select = int(len(structures) * n)
    selected = np.random.choice(struct_list, n_select,
                                replace=False, p=probab_list)
    return selected.tolist()


def minimize_combinations(structures):
    """
  if we have X structures and combinable information for ALL of them, we can
  can pass a subset of structures to this function to reduce the combinable
  information to to only the structures in the subset
  """
    ids = [s.id for s in structures]

    for s in structures:
        for c in s.connecting:
            logging.info("combinables before: {}".format(c.combinable))
            for s2_id, s2_c in reversed(c.combinable):
                if s2_id not in ids:
                    c.combinable.remove((s2_id, s2_c))
            logging.info("combinables after: {}".format(c.combinable))


if __name__ == '__main__':
    print("- Parsing args")
    opt, args = parse_args(sys.argv[1:])
    print("- Setting recursion limit")
    sys.setrecursionlimit(10000)  # required for some of the operations

# # make sure the output directory exists, otherwise create it
# Path("output/structures/").mkdir(parents=True, exist_ok=True)
# Path("output/levels/").mkdir(parents=True, exist_ok=True)

    # construct output directory paths
    print("- Getting current time")
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_dir = f"o_{opt.output_number}_n_{opt.n}_d_{opt.d}_m_{opt.min_structures}__{current_time}"

    structures_output_dir = Path(f"output/{output_dir}/structures")
    levels_output_dir = Path(f"output/{output_dir}/levels")

    # create directories if they don't exist
    print("- Creating output directories")
    structures_output_dir.mkdir(parents=True, exist_ok=True)
    levels_output_dir.mkdir(parents=True, exist_ok=True)

    print("- Getting level data")
    data = get_level_paths(opt)

    # g_s, g_f, structures = load_structures()
    print("- Extracting structures")
    g_s, g_f, structures = extract_structures(data)

    # logging.info("Num of structures before subset: {}".format(len(structures)))
    # structures = get_subset(structures)
    # logging.info("Num of structures after subset: {}".format(len(structures)))
    # minimize_combinations(structures + [g_s, g_f])

    selected = [s.id for s in structures]
    logging.info("Selected structures: {}".format(selected))

    print("- Computing structure combinations")
    structure_matching.compute_combinations(structures + [g_s, g_f])

    print("- Saving structures")
    save_structures(g_s, g_f, structures, structures_output_dir)

    analyze_structures(structures_output_dir)
    save_structures_data(f"output/{output_dir}/structures_data.csv")

    if opt.generate == "True":
        for n in range(opt.output_number):
            logging.info("Generating level {}".format(n))
            print(f"Generating level {n}")

            start_time = time.time()

            try:
                level, stats, structures_used, backtrack_count, used_stuctures = level_generation.generate_level(
                    structures, g_s, g_f, opt.min_structures)
            except EnvironmentError:
                print("Environmet Error!")
                continue

            duration = time.time() - start_time

            level_data = level.matrix_representation()
            # print(*level_data, sep='\n')

            generation_times.append(duration)
            leniencies.append(calculate_leniency(level_data))
            linearities.append(calculate_linearity(level_data))
            line_distances.append(calculate_line_distance(level_data))
            backtrackings.append(backtrack_count)

            structures_used_list.append(structures_used)
            structures_count_list.append(len(used_stuctures))
            level_lengths.append(len(level_data[0]))
            used_structures_list.append([s.id for s in used_stuctures])

            level_path = f"{levels_output_dir}/level_{n}.txt"
            level.save_as_level(level_path)

            if opt.render == "True":
                print("Rendering level {}".format(n))
                render_structure(level_path, f"{levels_output_dir}/level_{n}.png")

        save_data(f'output/{output_dir}')
        # print(generation_times)
