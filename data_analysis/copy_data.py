# Get a list of all directories inside the "output" directory
import os
import shutil

output_directory = '../output'
directories = [name for name in os.listdir(output_directory) if os.path.isdir(os.path.join(output_directory, name))]


if __name__ == "__main__":
    os.mkdir("levels_data")
    os.mkdir("structures_data")
    for directory in directories:
        try:
            print(f"moving {directory}")

            shutil.copyfile(f"{output_directory}/{directory}/data_collected.csv", f"levels_data/{directory}.csv")
            shutil.copyfile(f"{output_directory}/{directory}/structures_data.csv", f"structures_data/{directory}.csv")
        except Exception as e:
            print(e)
