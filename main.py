import string
import random

# input => experiment, database, conc, file sizes

# output => relevant vizs, logs
def ingest_inputs(): # take in config metrics from the yam file
    pass


def generate_rand_bytes(size):
    return bytes(random.choices(range(256), k=size))

def exp_lib():
    pass


def run_exps(): # to be run by the driver
    # size, exps to run, concurrency limit
    # invoke lambdas
    # 
    pass

# Example usage:
size_in_bytes = 100
byte_sequence = generate_rand_bytes(size_in_bytes)
print(byte_sequence)