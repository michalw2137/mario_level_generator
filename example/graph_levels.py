import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn import preprocessing


def plot_based_on_result(x, y, color='#1f77b4', shape='.'):
    print("\tnormalizing values")
    normalised_linearities = preprocessing.normalize(np.array([x]), norm='max')
    normalised_leniencies = preprocessing.normalize(np.array([y]), norm='max')

    x = normalised_linearities[0]
    y = normalised_leniencies[0]

    print("\tplotting succesful values")
    plt.plot(0, 0, 'w.')
    plt.plot(1, 1, 'w.')
    plt.plot(normalised_linearities, normalised_leniencies, shape, c=color)


def graph(directory: str, n: int):
    csv_path = f"{directory}/csv/n{n}.csv"
    print("\treading " + csv_path)
    data = pd.read_csv(csv_path)

    # separate based on result
    successful_levels = data[data['result'] == 1]
    failed_levels = data[data['result'] == 0]

    print(f"\t\tFailed levels: {len(failed_levels)}")
    print(f"\t\tSuccesful levels: {len(successful_levels)}")

    plot_based_on_result(successful_levels[directory], successful_levels["leniency"])
    plot_based_on_result(failed_levels[directory], failed_levels["leniency"], "orange", 'x')

    # plt.title(f"n = {n} {directory}")
    plt.xlabel(directory)
    plt.ylabel("leniency")

    plt.legend(labels=[f"n {n}", f"failed: {len(failed_levels)}", f"completed: {len(successful_levels)}"])

    print("\tsaving plot")
    plt.savefig(f"{directory}/plot/n{n}.png")
    plt.close()


if __name__ == "__main__":
    for n in range(15, 70, 5):
        print(f"Graphing linearity for n={n}")
        graph("linearity", n)

        print(f"Graphing line_distance for n={n}")
        graph("line_distance", n)
