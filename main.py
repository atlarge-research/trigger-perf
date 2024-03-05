import boto3
import time
from datetime import datetime
import yaml
import csv
from progressbar import progressbar

from utils.utils import *
from utils.data_proc import *
from utils.viz import *
from aws.aws import *
from drivers.s3_driver import *

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
    "num_readers": test_configs['num_readers']
}


# save_run_details(payload, "./logs/run_logs.csv")

# print(payload)
def main(payload):

    run_start_time = time.time()
    print(f"\nRUN START_TIME: {run_start_time}")
    print(f"RUN ID: {run_id}\n")
    time.sleep(3)
    # Invokes the Initial lmd 
    lambda_invoke('initial-lmd', payload)

    # Create a SNS notification to indicate initial-lmd completion

    
    # Sleeping for full chain to complete
    print("Waiting for full chain to complete")
    time.sleep(50)

    # Get the lambda logs
    print(f"Getting Lambda logs....")
    for i in progressbar(range(100)):# sleeoing 250 secs
        time.sleep(2.5) 
    get_lambda_logs("write-lmd", run_start_time, run_id)
    # time.sleep(75)
    get_lambda_logs("read-lmd", run_start_time, run_id)
    

    # Data processing
    latencies = calc_latency("./logs/write-lmd_logs.csv", "./logs/read-lmd_logs.csv", run_id)
    print(latencies)
    gen_box_plot(latencies, run_id) 
        

    return 0


if __name__ == "__main__":
    acc_id = 133132736141
    # print(calc_latency("./logs/write-lmd_logs.csv", "./logs/read-lmd_logs.csv","c109e7b9af"))
    main(payload)
    # get_lambda_logs("read-lmd", 1709630688.1948102, '3c55d5a165')
    
    # latencies = calc_latency("./logs/write-lmd_logs.csv", "./logs/read-lmd_logs.csv", '22c865e')
    # print(latencies)
    # gen_box_plot(latencies, "22c865e")
    


##Todo
    # poll logs until results
    # setup check
    # iter changes
    # Dynamo full run completion
    # complete run_logging
    # progress bar for waiting
    
