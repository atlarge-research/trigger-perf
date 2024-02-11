import string
import random
import boto3
import time
import subprocess

import ingest

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

def run_aws_command(cmd):
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        return  result.stdout.strip()
    except subprocess.CalledProcessError as err:
        print(f"Command failed: {cmd}, Error: {err}")
        return None



def setup_services(): # Set up lambda functions & data store

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


def read_from_s3(bucket):
    resp = s3.get_object(Bucket=bucket, )


def main():
    key = generate_rand_bytes(5)
    val = generate_rand_bytes(50)

    write_to_s3('buczy-bucket',key,val)

    return

if __name__ == "__main__":

    main()

# curl -X POST -H "Content-Type: application/json" -d '{"writes": "value69", "keys": "value70"}' https://opw4dj08ul.execute-api.eu-north-1.amazonaws.com/default/send-lambda
