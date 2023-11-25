import pandas as pd

if __name__ == "__main__":
    for n in [15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65]:
        file_path = f"logs/n{n}.txt"
        print(f"parsing {file_path}")

        level_names = []
        run_results = []
        block_reached = []
        total_length = []
        times = []

        df = pd.DataFrame(columns=['level', 'result', 'block_reached', 'total_length', 'time'])

        with open(file_path) as log_file:
            # parse all lines and store results in lists
            for line in log_file:
                if "level_" in line:
                    splitted = line.split(sep=' ')

                    # .split() leaves '' between spaces, remove them
                    while '' in splitted:
                        splitted.remove('')

                    # 0 - filename - level_0.txt
                    # 1 - result - 0 (or 1)
                    # 2 - block reached/total length - 32/202
                    # 3 - time:
                    # 4 - time in seconds - 45\n

                    level_names.append(splitted[0])
                    run_results.append(splitted[1])

                    blocks = splitted[2].split('/')
                    block_reached.append(blocks[0])

                    # total length is 1 too high
                    length = int(blocks[1]) - 1
                    total_length.append(length)

                    # splitted[4] is 40\n, remove newline
                    last_element = splitted[4]
                    time = last_element.split('\n')[0]

                    times.append(time)

            print("  - creating data frame")
            df['level'] = level_names
            df['result'] = run_results
            df['block_reached'] = block_reached
            df['total_length'] = total_length
            df['time'] = times

            print("  - saving data frame")
            df.to_csv(f'csv/n{n}.csv', index=False)
            print("  - data frame succesfully saved")
