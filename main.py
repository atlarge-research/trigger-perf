import boto3
import time
import subprocess
import yaml

from utils.utils import *
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



# print(payload)
def main(payload):

    run_start_time = time.time()
    # print(f"RUN START_TIME: {run_start_time}\n")

    time.sleep(3)
    # Invokes the Initial lmd 
    lambda_invoke('initial-lmd', payload)

    # Create a SNS notification to indicate initial-lmd completion


    # Sleeping for full chain to complete
    time.sleep(75)

    # Get the lambda logs
    print(f"RUN ID: {run_id}")
    # get_lambda_logs("write-lmd", run_start_time, run_id)
    # time.sleep(75)
    # get_lambda_logs("read-lmd", run_start_time, run_id)
    
    # time.sleep(5)
    # latencies = calc_latency("logs/write-lmd_logs.csv", "logs/read-lmd_logs.csv")
    
    
    return 0

if __name__ == "__main__":
    acc_id = 133132736141
    # main(payload)
    create_lambda_function(acc_id, "read-lmd")


##Todo
    # Role creation
    # setup check 
    # Dynamo setup
    # data processing functions
    
