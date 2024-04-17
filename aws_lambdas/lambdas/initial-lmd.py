import boto3
import json
import hashlib
import os
import time

def ds_write_lmd_func(key, data, ds, e_id, run_id):
        client = boto3.client('lambda')
        payload = [key, data, e_id, run_id, ds]
        response = client.invoke(
        FunctionName='write-lmd',
        InvocationType='Event',
        Payload=json.dumps(payload)
        )
        if response.get('FunctionError'):
            print(f"Error invoking write-lmd: {response.get('FunctionError')}")
        return response
    
    
def get_size(input_string):
    # Calculate the size of the input string in bytes
    string_bytes = input_string.encode('latin-1')  # Encode string to bytes
    size_in_bytes = len(string_bytes)
    return size_in_bytes

def generate_rand_string(size: int):
    # size is in bytes
    random_bytes = os.urandom(size)
    random_string = random_bytes.decode('latin-1')  # Decode bytes to string
    return random_string
    
'''
Generates a random event id for every write-lmd event
by hashing the timestamp and a salt.
return: a unique id of 7 bytes as str
'''
def gen_event_id():
    salt = '123'
    time_stamp = f"{str(time.time())}{salt}"
    e_id = hashlib.md5(time_stamp.encode()).hexdigest()[:7] 
    return e_id

'''
Generates a prefixed key of given size with the first 10 bytes
as the run_id.
'''
def gen_prefix_key(ksize: int, id: str):
    if ksize > get_size(id): # if required ksize > 10bytes
        rem_size = ksize - get_size(id)
        rem_key = generate_rand_string(rem_size)
        prefixed_key = id + rem_key
        return prefixed_key
    else:
        return id

def lambda_handler(event, context):
    
    # Get w-k-r input
    print('EVENT: ', event)
    run_id = event.get('run_id')
    data_store = event.get('data_store')
    num_keys = int(event.get('num_keys'))
    ksize_start = int(event.get('ksize_start'))
    ksize_end = int(event.get('ksize_end'))
    kjumps = int(event.get('kjumps'))
    vsize = int(event.get('vsize'))
    num_readers = int(event.get('num_readers'))
    iters = int(event.get('iters'))
    
    # Get key sizes required
    key_sizes_to_write = json.loads(event.get('ksizes_list')) # when ksizes are passed as list in config
    # key_sizes_to_write = []
    # temp = ksize_start

    # while temp < ksize_end:
    #     key_sizes_to_write.append(temp)
    #     temp += kjumps
        
    # Key and data generation
    for i in key_sizes_to_write:
        print(f"In key_sizes_to_write loop for key {i}, type: {type(i)}")
        # i = int(i)
        for j in range(iters): #iters to be run
            e_id = gen_event_id()
            key = gen_prefix_key(i, run_id) # Key prefixed with run id (10 bytes)
            data = gen_prefix_key(vsize, e_id) # Data prefixed with event id (10 bytes)
            
            # Invoke send/write function
            print(f"INVOKING KEY SIZE: {i}\n")
    
            resp = ds_write_lmd_func(key,data, data_store,e_id,run_id)
            time.sleep(1)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

   