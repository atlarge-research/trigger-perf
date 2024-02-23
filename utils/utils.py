import yaml
import random
import time
import hashlib
import os
import uuid
import pandas as pd

def read_config(file_path: str):
    with open(file_path, 'r') as file:
        yload = yaml.safe_load(file)
    return yload

def generate_rand_bytes(size):
    return str(bytes(random.choices(range(256), k=size)))

'''
Get the data from the write & read csv files into a pandas df.
returns: all logs from write&read lmds sorted by e_id.
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


def generate_rand_string(size: int):
    # size is in bytes
    random_bytes = os.urandom(size)
    random_string = random_bytes.decode('latin-1')  # Decode bytes to string
    return random_string

def get_size(input_string: str):
    # Calculate the size of the input string in bytes
    string_bytes = input_string.encode('latin-1')  # Encode string to bytes
    size_in_bytes = len(string_bytes)
    return size_in_bytes


'''
Generates a random run_id for every time the system in run
by hashing the run start timestamp and a salt.
return: a unique run_id of 10 bytes as str
'''
def gen_run_id():
    salt = 'abc'
    time_stamp = f"{str(time.time())}{salt}"
    run_id = hashlib.md5(time_stamp.encode()).hexdigest()[:9] + "/"
    return run_id

'''
Generates a prefixed key of given size with the first 10 bytes
as the run_id.
'''
def gen_prefix_key(ksize: int, run_id: str):
    if ksize > 10: # if required ksize > 10bytes
        rem_size = ksize - 10
        rem_key = generate_rand_string(rem_size)
        prefixed_key = run_id + rem_key
        return prefixed_key
    else:
        return run_id

def extract_run_id(prefix_key: str):
    pass



# pkey = gen_prefix_key(15)
# print(pkey)
# # salt = 'abc'
# print(get_size(pkey))

# def main():
#     configs = read_config('../config.yaml')
#     print(configs['data_store'])
#     pass

# if __name__ == "__main__":
#     main()