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


def analyze_data(data_frame, parameter_value):
    # Calculate summary statistics
    summary_stats = data_frame.describe(include="all")
    # Exclude the count row from the summary statistics
    summary_stats = summary_stats.drop("count")
    print(f"\n\n\nSummary Statistics for {parameter_value}:")
    print(summary_stats)

    # Define the number of rows and columns for subplots
    num_rows = 2
    num_cols = 4

    # Create subplots
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, 15))

    # Flatten the axes array
    axes = axes.flatten()

    # Plot histograms for each column
    for i, column in enumerate(data_frame.columns):
        axes[i].hist(data_frame[column])
        axes[i].set_title(f'Histogram of {parameter_value}: {column}')
        axes[i].set_xlabel(column)
        axes[i].set_ylabel('Frequency')

    # Adjust spacing between subplots
    fig.tight_layout()

    # Create a directory for saving the histograms
    save_directory = os.path.join("output", "all_columns")
    os.makedirs(save_directory, exist_ok=True)
    # Save the figure to the specified directory
    save_path = os.path.join(save_directory, f"{parameter_value}_histograms.png")

    plt.savefig(save_path)  # Save the figure before showing and closing
    plt.show()  # Show the figure
    plt.close()  # Close the figure


# directories = ['o_100_n_20_d_4_m_35__2023-06-20_10-05-29',
#                'o_100_n_35_d_4_m_35__2023-06-20_00-26-32',
#                'o_100_n_50_d_4_m_35__2023-06-20_00-28-24',
#                'o_100_n_20_d_4_m_35__2023-06-20_10-16-08',
#                'o_100_n_35_d_4_m_35__2023-06-20_10-15-02',
#                'o_100_n_50_d_4_m_35__2023-06-20_10-13-00']

# Get a list of all directories inside the "output" directory
output_directory = '../output'
directories = [name for name in os.listdir(output_directory) if os.path.isdir(os.path.join(output_directory, name))]

dataframes = []

if __name__ == "__main__":
    for directory in directories:
        try:
            dataframe = load_csv_into_dataframe(directory)
            dataframes.append(dataframe)
            n_parameter = directory.split("_")[3]
            generation_time = directory.split("_")[10]
            analyze_data(dataframe, f"n={n_parameter} [{generation_time}]")
        except:
            print("no data file")