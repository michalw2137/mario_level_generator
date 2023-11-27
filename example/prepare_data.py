import os

import pandas as pd

if __name__ == "__main__":
    levels_data_dir = "../data_analysis/levels_data/"

    for file in os.listdir(levels_data_dir):
        # retrieve n value from file name
        n = file.split('_')[3]
        print(n, file)

        run_results = pd.read_csv(f"data/n{n}.csv")
        metrics = pd.read_csv(levels_data_dir + file)

        prepared_linearity = pd.DataFrame(columns=['linearity', 'leniency', 'result'])
        prepared_line_distance = pd.DataFrame(columns=['line_distance', 'leniency', 'result'])

        prepared_linearity['linearity'] = metrics['linearity']
        prepared_linearity['leniency'] = metrics['leniency']
        prepared_linearity['result'] = run_results['result']

        prepared_line_distance['line_distance'] = metrics['line_distance']
        prepared_line_distance['leniency'] = metrics['leniency']
        prepared_line_distance['result'] = run_results['result']

        prepared_linearity.to_csv(f"linearity/csv/new_n{n}.csv", index=False)
        prepared_line_distance.to_csv(f"line_distance/csv/new_n{n}.csv", index=False)
