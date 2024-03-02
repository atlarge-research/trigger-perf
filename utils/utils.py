import yaml
import random
import time
import hashlib
import os
import pandas as pd
from datetime import datetime

def read_config(file_path: str):
    with open(file_path, 'r') as file:
        yload = yaml.safe_load(file)
    return yload

def generate_rand_bytes(size):
    return str(bytes(random.choices(range(256), k=size)))


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
return: a unique run_id of 10 bytes as str
'''
def gen_run_id():
    salt = 'abc'
    time_stamp = f"{str(time.time())}{salt}"
    run_id = hashlib.md5(time_stamp.encode()).hexdigest()[:10] 
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

# if __name__ == "__main__":
#     main()