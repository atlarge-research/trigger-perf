import yaml
import random
import pandas as pd

def read_config(file_path):
    with open(file_path, 'r') as file:
        yload = yaml.safe_load(file)
    return yload

def generate_rand_bytes(size):
    return str(bytes(random.choices(range(256), k=size)))

'''
Get the data from the write & read csv files into a pandas df
returns: all logs from write&read lmds sorted by e_id
'''
def prep_logs_data(write_csv_path, read_csv_path):
    w_df = pd.read_csv(write_csv_path)
    r_df = pd.read_csv(read_csv_path)
    full_df = pd.concat([w_df, r_df], ignore_index=True)
    # sorted_df = full_df.sort_values(by='e_id')
    return w_df, r_df

'''
latency = readfn_start_time - s3_put_time
'''
def calc_latency(w_csv_path, r_csv_path):
    w_df, r_df = prep_logs_data(w_csv_path, r_csv_path)
    
    s3_put_times = w_df['put_time']
    rlmd_start_times = r_df['exec_start_time']
    print(rlmd_start_times)
    print(s3_put_times)
    latencies = []
    for i in range(0,len(rlmd_start_times)):
        latency = rlmd_start_times[i] - s3_put_times[i]
        latencies.append(latency)

    return latencies


# def main():
#     configs = read_config('../config.yaml')
#     print(configs['data_store'])
#     pass

# if __name__ == "__main__":
#     main()