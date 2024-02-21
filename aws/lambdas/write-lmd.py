import time
import boto3
import json
import logging
import sys


def get_size(data):
    size = sys.getsizeof(data)
    return size

# need to enable versioning to gaurantee a notification for every event
def lambda_handler(event, context):

    # writing to s3
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    recv_time = time.time()

    file_key = event[0]
    data_to_write = event[1]
    e_id = event[3]
    ksize = get_size(file_key)
    vsize = get_size(data_to_write)
    s3_client = boto3.client('s3')
    s3_bucket = 'test-buck-xyz'
    metadata = {'e_id': e_id}
    s3_put_time = time.time()
    s3_client.put_object(
        Bucket=s3_bucket,
        Key=file_key,
        Body=json.dumps(data_to_write),
        Metadata=metadata,
        ContentType='application/json'
    )
    
    # TBE = to be extracted
    log_data = {
        'e_id': e_id,
        'event': 'TBE',
        'execution_start_time': recv_time,
        's3_put_time': s3_put_time,
        'key': file_key,
        'key_size': ksize,
        'value_size': vsize
    }
    # logger.info(f"TBE , Write Lambda execution started at: {recv_time}, Write-lmd s3 put time: {s3_put_time}, Key: {file_key}, KeySize: {ksize}, ValSize: {vsize}")
    logger.info(json.dumps(log_data))

    return {
        'statusCode': 200,
        'body': 'Lambda executed successfully!',
        's3_put_time': s3_put_time,
        # 's3_event_time': s3_event_time,
        'lambda_execution_start_time': recv_time
    }

# curl -X POST -H "Content-Type: application/json" -d '{"data": "key-val-pair", "writes": "value69", "keys": "value70"}' https://opw4dj08ul.execute-api.eu-north-1.amazonaws.com/default/send-lambda
