import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# Set the Pandas display options to show all columns
pd.set_option('display.max_columns', None)
# Set the Pandas display options to disable scientific notation
pd.set_option('display.float_format', '{:.2f}'.format)
# Set the Pandas display options to exclude count
pd.set_option('display.show_dimensions', False)


def load_csv_into_dataframe(middle_directory):
    csv_path = os.path.join('..', 'output', middle_directory, 'data_collected.csv')
    df = pd.read_csv(csv_path)
    return df


def analyze_data(data_frame, directory_name):
    # Calculate summary statistics
    summary_stats = data_frame.describe(include="all")
    # Exclude the count row from the summary statistics
    summary_stats = summary_stats.drop("count")
    print(f"\n\n\nSummary Statistics for {directory_name}:")
    print(summary_stats)

    # Plot histograms for all columns
    for column in data_frame.columns:
        data_frame[column].plot(kind='hist')
        plt.title(f'Histogram of {directory_name}: {column}')
        plt.xlabel(column)
        plt.ylabel('Frequency')

        # Create a directory for saving the histograms of each column
        save_directory = os.path.join("output", column)
        os.makedirs(save_directory, exist_ok=True)
        # Save the histogram to the specified directory
        save_path = os.path.join(save_directory, f"{directory_name}_histogram.png")

        plt.savefig(save_path)  # Save the figure before showing and closing
        plt.show()  # Show the figure
        plt.close()  # Close the figure


directories = ['o_100_n_15_d_4_m_35__2023-06-20_00-27-40',
               'o_100_n_35_d_4_m_35__2023-06-20_00-26-32',
               'o_100_n_50_d_4_m_35__2023-06-20_00-28-24']

dataframes = []

if __name__ == "__main__":
    for directory in directories:
        dataframe = load_csv_into_dataframe(directory)
        dataframes.append(dataframe)
        n_parameter = directory.split("_")[3]
        analyze_data(dataframe, f"n={n_parameter}")
