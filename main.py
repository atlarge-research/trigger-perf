import string
import random
import boto3
import time

# input => experiment, database, conc, file sizes
s3 = boto3.client('s3')
# output => relevant vizs, logs
def ingest_inputs(): # take in config metrics from the yam file
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