import time
import boto3
import json
import logging
import sys


def get_size(input_string):
    # Calculate the size of the input string in bytes
    string_bytes = input_string.encode('latin-1')  # Encode string to bytes
    size_in_bytes = len(string_bytes)
    return size_in_bytes

# need to enable versioning to gaurantee a notification for every event
def lambda_handler(event, context):

    # writing to s3
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    recv_time = time.time()

    file_key = event[0]
    data_to_write = event[1]
    e_id = event[2]
    ksize = get_size(file_key)
    vsize = get_size(data_to_write)
    s3_client = boto3.client('s3')
    s3_bucket = 'test-buck-xyz'
    metadata = {'e_id': str(e_id)}
    s3_put_time = time.time()
    resp = s3_client.put_object(
        Bucket=s3_bucket,
        Key=file_key,
        Body=json.dumps(data_to_write),
        Metadata=metadata,
        ContentType='application/json'
    )

    # Get aws x-ray request-id
    xar_id = resp['ResponseMetadata']['HTTPHeaders']['x-amz-request-id']
    
    log_data = {
        'xar_id': xar_id,
        'event': 'WRITE',
        'exec_start_time': recv_time,
        'put_time': s3_put_time,
        'key': file_key,
        'key_size': ksize,
        'value_size': vsize
    }
    
    logger.info(json.dumps(log_data))

    return {
        'statusCode': 200,
        'body': 'Lambda executed successfully!',
    }

# curl -X POST -H "Content-Type: application/json" -d '{"data": "key-val-pair", "writes": "value69", "keys": "value70"}' https://opw4dj08ul.execute-api.eu-north-1.amazonaws.com/default/send-lambda
