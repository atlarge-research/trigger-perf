import boto3
import time
from datetime import datetime
import yaml
import csv
from tqdm import tqdm

from utils.utils import *
from utils.data_proc import *
from utils.viz import *
from drivers.aws import *
from drivers.s3_driver import *

# To read config file
def read_config(file_path):
    with open(file_path, 'r') as file:
        yload = yaml.safe_load(file)
    return yload

# Load Configs
test_configs = read_config('config.yaml')
run_id = gen_run_id()
data_store = test_configs['data_store']
payload = {
    "run_id": run_id,
    "data_store": test_configs['data_store'],
    "num_keys": test_configs['key']['num'],
    "ksize_start": test_configs['key']['size_start'],
    "ksize_end": test_configs['key']['size_end'],
    "kjumps": test_configs['key']['jumps'],
    "vsize": test_configs['value']['size'],
    "num_readers": test_configs['num_readers'],
    "ksizes_list": test_configs['key']['sizes_list'],
    "iters": test_configs['num_iters']
}


# save_run_details(payload, "./logs/run_logs.csv")


# print(payload)
def main(payload):
    
    ds = test_configs['data_store']
    num_iters = test_configs['num_iters']
    print(f"\n{ds} experiment for {num_iters} iterations")

    run_start_time = time.time()
    print(f"\nRUN START_TIME: {run_start_time}")
    print(f"RUN ID: {run_id}\n")
    time.sleep(3)

    # Invokes the Initial lmd 
    lambda_invoke('initial-lmd', payload)

    # Create a SNS notification to indicate initial-lmd completion

    
    # Sleeping for full chain to complete
    print("Waiting for full chain to complete...")
    time.sleep(20) #50 is a good number

    # Get the lambda logs
    print(f"Getting Lambda logs....")
    for i in tqdm(range(100), desc="Getting Lambda logs....."):
        time.sleep(2) # 4 is a good number
    get_lambda_logs("write-lmd", run_start_time, run_id)
    # time.sleep(75)
    # get_lambda_logs("pg-recv", run_start_time, run_id) #change to pg-recv for aurora else read-lmd
    
    # Dynamo Data processing
    # latencies = calc_latency("./logs/write-lmd_logs.csv", "./logs/read-lmd_logs.csv", run_id)
    # print(latencies)
    # ksizes_list = test_configs['key']['sizes_list']
    # gen_box_plot(latencies, run_id, ksizes_list) 
        
    return 0


if __name__ == "__main__":
    acc_id = 133132736141
    # main(payload)
    get_lambda_logs("pg-recv", 1713886807.586133, 'f72a4b7')
    # latencies = calc_latency("./logs/write-lmd_logs.csv", "./logs/read-lmd_logs.csv", 'e41e876')
    # print(latencies)
    # gen_box_plot(latencies, "b8396a3", [10, 20, 40, 80, 120, 160])
    


'''
Notes
------
1) Key and value size should be a minimum of 10 bytes.
   If needed otherwise, run and event id generation functions have to be modified
2) 


'''
    
