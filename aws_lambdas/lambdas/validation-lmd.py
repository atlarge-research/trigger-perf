import time
import boto3
import json
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

'''
Puts the key and data into dynamo table
returns: log_data as a dict
'''
def dynamo_put_handler(file_key, data, h_arr):
    region = 'us-east-1'
    table_name = "trigger-perf"
    dynamodb = boto3.client('dynamodb', region_name=region)
    item = {
    'id': {'S': file_key},    
    'value': {'S': data}  
    }

    try:
        put_time = time.time()
        resp = dynamodb.put_item(
            TableName=table_name,
            Item=item
        )
        
        log_data = {
            'run_id': h_arr[0],
            'e_id': h_arr[4],
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

'''
Puts the key and data into s3 bucket
returns: log_data as a dict
'''
def s3_put_handler(file_key, data, h_arr):
    s3_client = boto3.client('s3')
    s3_bucket = 'test-buck-ritul'
    metadata = {'e_id': str(0)} # Remove later
    try:
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
        # 'run_id': h_arr[0],
        'run_id': xar_id, # xar_id is used as 
        'e_id': h_arr[4],
        'event': 'WRITE',
        'exec_start_time': h_arr[3],
        'put_time': put_time,
        'key': file_key,
        'key_size': h_arr[1],
        'value_size': h_arr[2]
        }
        return log_data
    except Exception as e:
        print(f"S3 put event failed: {e}")

'''
does what Write lmd does
'''
def write_lmd_handler(event, context):

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    wfn_start_time = time.time()

    file_key = event[0]
    data_to_write = event[1]
    e_id = event[2]
    run_id = event[3]
    ds = event[4]
    event_iter = event[5]
    ksize = get_size(file_key)
    print(f"KEY SIZE RECEIVED: {ksize}")
    vsize = get_size(data_to_write)
    handler_arr = [run_id, ksize, vsize, wfn_start_time, e_id, event_iter]

    # Putting object into required data store
    if ds == "s3":
        log_data = s3_put_handler(file_key, data_to_write, handler_arr)
    elif ds == "dynamo":
        log_data = dynamo_put_handler(file_key, data_to_write, handler_arr)
    
    logger.info(json.dumps(log_data))

    return {
        'statusCode': 200,
        'body': 'Lambda executed successfully!'
    }


def lambda_handler(event, context):
    recv_time = time.time()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    print(event)
    if 'Records' in event and len(event['Records']) > 0 and 'eventSource' in event['Records'][0] and event['Records'][0]['eventSource'] == 'aws:s3':
        # S3 event notification detected
        print("!@!@! Triggered by an S3 event!")
        log_data = s3_recv_handler(event, recv_time)
        logger.info(json.dumps(log_data))
    elif 'Records' in event and event['Records'][0]['eventSource'] == 'aws:dynamodb':
        # Dynamo event notification detected
        print("!@!@! Triggered by an Dynamo event!")
        log_data = dynamo_recv_handler(event, recv_time)
        logger.info(json.dumps(log_data))
    else:
        print("Lambda triggered for write!")
        write_lmd_handler(event, context)
    
    return {
        'statusCode': 200,
        'body': 'Lambda executed successfully!'
    }