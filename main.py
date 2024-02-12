import string
import random
import boto3
import time
import subprocess

import ingest
from aws import *

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
    test_configs = ingest.read_config(file)
    data_store = test_configs['data_store']
    num_writers = test_configs['num_writers']
    num_keys = test_configs['num_keys']
    key_size = test_configs['key_size']
    value_size = test_configs['value_size']
    num_readers = test_configs['num_readers']
    pass





def setup_services(): # Set up lambda functions & data store

    print("## Setup process started")
    # Setup Role ###TBD

    # Initial lambda setup
    create_lambda_function(acc_id, "initial-lmd")

    # Write lambda setup
    create_lambda_function(acc_id, "write-lmd")

    # Datastore setup

    # Read lambda setup
    create_lambda_function(acc_id, "read-lmd")


    pass

def generate_rand_bytes(size):
    return str(bytes(random.choices(range(256), k=size)))

def write_to_s3(bucket, key, val):
    
    inv_time = str(time.perf_counter())
    try:
        s3.put_object(Key=key, Body=val, Bucket=bucket, Metadata={'invocation-time': inv_time})
        print(f"Successfully wrote key-value pair to S3: {key} -> {val}\n")
    except Exception as e:
        print(f"error writing to s3: {e}")

    print(f'invocation time: {inv_time}')
    return





def main():
    key = generate_rand_bytes(5)
    val = generate_rand_bytes(50)

    write_to_s3('buczy-bucket',key,val)

    return

if __name__ == "__main__":

    main()

# curl -X POST -H "Content-Type: application/json" -d '{"writes": "value69", "keys": "value70"}' https://opw4dj08ul.execute-api.eu-north-1.amazonaws.com/default/send-lambda
