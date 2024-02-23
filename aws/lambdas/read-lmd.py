import time
import json
import boto3
import logging

def get_size(input_string):
    # Calculate the size of the input string in bytes
    string_bytes = input_string.encode('latin-1')  # Encode string to bytes
    size_in_bytes = len(string_bytes)
    return size_in_bytes

def lambda_handler(event, context):

    ## After s3 trigger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    print('XAR-ID\n')
    print(event['Records'][0]['responseElements']['x-amz-request-id'])
    readfn_start_time = time.time()
    s3_event = event['Records'][0]['s3']
    bucket_name = s3_event['bucket']['name']
    object_key = s3_event['object']['key']
    xar_id = event['Records'][0]['responseElements']['x-amz-request-id']
    
    ksize = 0
    vsize = 0

    # time.sleep(5)
    log_data = {
        'xar_id': xar_id,
        'event': 'READ',
        'exec_start_time': readfn_start_time,
        'put_time': 0,
        'key': object_key,
        'key_size': ksize,
        'value_size': vsize
    }
    logger.info(json.dumps(log_data))

    return {
        'statusCode': 200,
        'body': 'Lambda executed successfully!'

    }
