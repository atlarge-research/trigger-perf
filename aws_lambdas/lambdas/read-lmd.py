import time
import json
import boto3
import logging

def get_size(input_string):
    # Calculate the size of the input string in bytes
    string_bytes = input_string.encode('latin-1')  # Encode string to bytes
    size_in_bytes = len(string_bytes)
    return size_in_bytes

'''
Used to extract the id prefixed in the key/value
'''
def extract_id(prefix_key: str, id_size: int):
    return prefix_key[:id_size]
    

def s3_recv_handler(event, readfn_start_time):
    s3_event = event['Records'][0]['s3']
    bucket_name = s3_event['bucket']['name']
    object_key = s3_event['object']['key']
    xar_id = event['Records'][0]['responseElements']['x-amz-request-id']
    ksize = get_size(object_key)
    vsize = 0

    log_data = {
        'run_id': xar_id, # xar_id is used as run_id
        'event': 'RECV',
        'exec_start_time': readfn_start_time,
        'put_time': 0,
        'key': object_key,
        'key_size': ksize,
        'value_size': vsize
    }
    return log_data

def dynamo_recv_handler(event,readfn_start_time):
    key = event['Records'][0]['dynamodb']['Keys']['id']['S']
    value = event['Records'][0]['dynamodb']['NewImage']['value']['S']
    ksize = get_size(key)
    vsize = get_size(value)
    
    # extract run_id from the key
    run_id = extract_id(key, 7)
    
    # extract e_id from the value
    e_id = extract_id(value, 7)

    log_data = {
        'run_id': run_id,
        'e_id': e_id,
        'event': 'RECV',
        'exec_start_time': readfn_start_time,
        'put_time': 0,
        'key': key,
        'key_size': ksize,
        'value_size': vsize
    }
    return log_data


def lambda_handler(event, context):

    readfn_start_time = time.time()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    print(event)    

    # check what datastore triggered this function & handle
    if event['Records'][0]['eventSource'] == 'aws:dynamodb':
        log_data = dynamo_recv_handler(event, readfn_start_time)
    elif 'Records' in event and 's3' in event['Records'][0]:
        log_data = s3_recv_handler(event, readfn_start_time)
        # insert logic to check if s3 or s3express 
    
    logger.info(json.dumps(log_data))

    return {
        'statusCode': 200,
        'body': 'Lambda executed successfully!'
    }
