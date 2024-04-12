import yaml
import random
import time
import hashlib
import os
import numpy as np
import pandas as pd
from datetime import datetime

def read_config(file_path: str):
    with open(file_path, 'r') as file:
        yload = yaml.safe_load(file)
    return yload

def generate_rand_bytes(size):
    return str(bytes(random.choices(range(256), k=size)))


# def generate_rand_string(size: int):
#     # size is in bytes
#     random_bytes = os.urandom(size)
#     random_string = random_bytes.decode('latin-1')  # Decode bytes to string
#     return random_string


def generate_rand_string(size: int):
    # size is in bytes
    random_bytes = os.urandom(size)
    random_string = random_bytes.decode('latin-1')  # Decode bytes to string
    random_string = random_string.replace('\n', '').replace('\r', '')  # Remove newline characters
    
    if len(random_string.encode('latin-1')) < size:
        padding = generate_rand_string(size - len(random_string.encode('latin-1')))
        random_string += padding

    return random_string

def get_size(input_string: str):
    # Calculate the size of the input string in bytes
    string_bytes = input_string.encode('latin-1')  # Encode string to bytes
    size_in_bytes = len(string_bytes)
    return size_in_bytes

'''
On a new run it saves the input payload as a row in ./logs/run_logs.csv
'''
def save_run_details(payload, path):
    dummy_payload = {
        "run_id": "Dummy entry",
        "data_store": "data_store_1",
        "num_keys": 100,
        "ksize_start": 10,
        "ksize_end": 100,
        "kjumps": 10,
        "vsize": 1024,
        "num_readers": 5,
        "datetime": "abc"
    }
    # check if path exists if not create csv with dummy row
    if not os.path.exists(path):
        print("here\n")
        dummy_df = pd.DataFrame([dummy_payload])
        dummy_df.to_csv(path, index=False)
    # Add run details to the csv 
    payload["time"] = datetime.now()
    run_df = pd.read_csv(path)
    updated_run_df = run_df.append(payload, ignore_index=True)
    updated_run_df.to_csv(path, index=False)




'''
Generates a random run_id for every time the system in run
by hashing the run start timestamp and a salt.
return: a unique run_id of 7 bytes as str
'''
def gen_run_id():
    salt = 'abc'
    time_stamp = f"{str(time.time())}{salt}"
    run_id = hashlib.md5(time_stamp.encode()).hexdigest()[:7] 
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

'''
Used to extract the id prefixed in the key/value
'''
def extract_id(prefix_key: str, id_size: int):
    return prefix_key[:id_size]
    

# pkey = gen_prefix_key(15)
# print(pkey)
# # salt = 'abc'
# print(get_size(pkey))

# def main():
#     configs = read_config('../config.yaml')
#     print(configs['data_store'])
#     pass

def get_size_utf8(input_string: str):
    # Calculate the size of the input string in bytes
    string_bytes = input_string.encode('latin-1')  # Encode string to bytes
    size_in_bytes = len(string_bytes)
    return size_in_bytes


def read_text_file(file_path):
    ksizes_arr = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                key = line.strip() 
                ksize = get_size_utf8(key)
                ksizes_arr.append(ksize)
        min_ks = min(ksizes_arr)
        max_ks = max(ksizes_arr)
        mean_ks = np.mean(ksizes_arr)
        median_ks = np.median(ksizes_arr)
        print(f"Min ksize = {min_ks}")
        print(f"Max ksize = {max_ks}")
        print(f"Mean ksize = {mean_ks}")
        print(f"Median ksize = {median_ks}")

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    check = get_size_utf8('/registry/apiregistration.k8s.io/apiservices/v1.admissionregistration.k8s.io')
    # print(check)
    read_text_file('kube-etcd-keys.txt')

'''
Min ksize = 27
Max ksize = 93
Mean ksize = 58.562886597938146
Median ksize = 59.0

'''
