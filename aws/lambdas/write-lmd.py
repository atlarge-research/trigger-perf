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


'''
Puts the key and data into s3 bucket
returns: log_data as a dict
'''
def s3_put_handler(file_key, data, h_arr):
    s3_client = boto3.client('s3')
    s3_bucket = 'test-buck-ritul'
    metadata = {'e_id': str(0)} # Remove later
    put_time = time.time()
    resp = s3_client.put_object(
        Bucket=s3_bucket,
        Key=file_key,
        Body=json.dumps(data),
        Metadata=metadata,
        ContentType='application/json'
    )
    xar_id = resp['ResponseMetadata']['HTTPHeaders']['x-amz-request-id']
    log_data = {
    'run_id': h_arr[0],
    'xar_id': xar_id,
    'event': 'WRITE',
    'exec_start_time': h_arr[3],
    'put_time': put_time,
    'key': file_key,
    'key_size': h_arr[1],
    'value_size': h_arr[2]
    }
    return log_data


def s3Express_put_object():
    pass


### TO complete dynamo put handler
'''
Puts the key and data into dynamo table
returns: log_data as a dict
'''
def dynamo_put_handler(file_key, data, h_arr):
    region = 'us-east-1'
    table_name = "trigger-perf"
    dynamodb = boto3.client('dynamodb', region_name=region)
    item = {
    'id': {'S': file_key},     # Assuming 'id' is the primary key of type String
    'value': {'S': data}  # Assuming 'value' is an attribute of type String
    }

    try:
        put_time = time.time()
        resp = dynamodb.put_item(
            TableName=table_name,
            Item=item
        )
        log_data = {
            'run_id': h_arr[0],
            # 'xar_id': xar_id,
            'event': 'WRITE',
            'exec_start_time': h_arr[3],
            'put_time': put_time,
            'key': file_key,
            'key_size': h_arr[1],
            'value_size': h_arr[2]
            }
        return log_data
    
    except Exception as e:
        print(f"ERROR: Failed to insert kv pair to dynamo, {str(e)}")
        print(resp)




# need to enable versioning to gaurantee a notification for every event
def lambda_handler(event, context):

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    wfn_start_time = time.time()

    file_key = event[0]
    data_to_write = event[1]
    e_id = event[2]
    run_id = event[3]
    ds = event[4]
    ksize = get_size(file_key)
    print(f"KEY SIZE RECVED: {ksize}")
    vsize = get_size(data_to_write)
    handler_arr = [run_id, ksize, vsize, wfn_start_time]

    # Putting object into required data store
    if ds == "s3":
        log_data = s3_put_handler(file_key,data_to_write, handler_arr)
    elif ds == "s3Express":
        pass
    elif ds == "dynamo":
        log_data = dynamo_put_handler(file_key,data_to_write, handler_arr)

    
    logger.info(json.dumps(log_data))

    return {
        'statusCode': 200,
        'body': 'Lambda executed successfully!',
    }

