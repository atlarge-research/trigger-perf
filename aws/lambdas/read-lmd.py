import time
import json
import boto3
import logging

def get_size(input_string):
    # Calculate the size of the input string in bytes
    string_bytes = input_string.encode('latin-1')  # Encode string to bytes
    size_in_bytes = len(string_bytes)
    return size_in_bytes

def s3_handler(event, readfn_start_time):
    s3_event = event['Records'][0]['s3']
    bucket_name = s3_event['bucket']['name']
    object_key = s3_event['object']['key']
    xar_id = event['Records'][0]['responseElements']['x-amz-request-id']
    ksize = get_size(object_key)
    vsize = 0

    log_data = {
        'xar_id': xar_id,
        'event': 'RECV',
        'exec_start_time': readfn_start_time,
        'put_time': 0,
        'key': object_key,
        'key_size': ksize,
        'value_size': vsize
    }
    return log_data

def dynamo_handler(event,readfn_start_time):
    pass
    # print('XAR-ID\n')
    # print(event['Records'][0]['responseElements']['x-amz-request-id'])

def lambda_handler(event, context):

    readfn_start_time = time.time()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    print(event)    

    # check what datastore triggered this function & handle
    if event['Records'][0]['s3']:
        log_data = s3_handler(event, readfn_start_time)
    elif event['Records'][0]['eventSource'] == 'dynamodb':
        log_data = dynamo_handler(event, readfn_start_time)
    
    logger.info(json.dumps(log_data))

    return {
        'statusCode': 200,
        'body': 'Lambda executed successfully!'
    }
