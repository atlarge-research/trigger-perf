import boto3
import time
import subprocess

from utils.utils import *
from aws.aws import *
from drivers.s3_driver import *

# input => experiment, database, conc, file sizes
s3 = boto3.client('s3')

# Configs
data_store = ""
num_writers = 0
num_keys = 0
key_size = 0
value_size = 0
num_readers = 0
num_iters = 5


def ingest_inputs(file): # take in config metrics from the yam file
    test_configs = read_config(file)
    data_store = test_configs['data_store']
    num_writers = test_configs['num_writers']
    num_keys = test_configs['num_keys']
    key_size = test_configs['key_size']
    value_size = test_configs['value_size']
    num_readers = test_configs['num_readers']
    pass



def main():
    key = generate_rand_bytes(5)
    val = generate_rand_bytes(50)
    acc_id = 471112959817
    payload = '{"writes": "1", "keys": "2", "reads": "3" }'

    # Invokes the Initial lmd 
    lambda_invoke('initial-lmd', payload)

    # Create a SNS notification to indicate initial-lmd completion


    # Sleeping for full chain to complete
    time.sleep(5)

    # Get the lambda logs
    get_lambda_logs('write-lmd')
    get_lambda_logs('read-lmd')

    return

if __name__ == "__main__":

    main()

# curl -X POST -H "Content-Type: application/json" -d '{"writes": "value69", "keys": "value70"}' https://opw4dj08ul.execute-api.eu-north-1.amazonaws.com/default/send-lambda
