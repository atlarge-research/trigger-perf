import time
import boto3
import json
import logging
import hashlib


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
Only two values that matter for the logging is event_iter(key) and put_time
'''
def aurora_put_handler(file_key, data, h_arr):
    region = 'us-east-1'
    cluster_arn = 'arn:aws:rds:us-east-1:133132736141:cluster:aurora-pg'
    secret_arn = 'arn:aws:secretsmanager:us-east-1:133132736141:secret:rds!cluster-69e731ac-3d92-4bd0-8107-cff996d47a37-YRzaMp'
    db_name = "postgres"
    table_name = 'kv_table'
    client = boto3.client('rds-data', region_name=region)


    sql_statement = f"""
        INSERT INTO {table_name} (key, value)
        VALUES (:key, :value)
    """
    event_iter = h_arr[5]
    put_time = time.time()
    parameters = [
        {'name': 'key', 'value': {'stringValue': str(event_iter)}},
        {'name': 'value', 'value': {'stringValue': str(put_time)}}
    ]
    
    try:
        resp = client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=db_name,
            sql=sql_statement,
            parameters=parameters
        )
        log_data = {
            'run_id': h_arr[0],
            'e_id': h_arr[4],
            'event': 'WRITE',
            'exec_start_time': h_arr[3],
            'put_time': put_time,
            'key': event_iter,
            'key_size': h_arr[1],
            'value_size': h_arr[2]
            }
        
        print("Data inserted successfully!")
        return log_data
    except Exception as e:
        print(f"ERROR inserting data: {e}")
    pass

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
    event_iter = event[5]
    ksize = get_size(file_key)
    print(f"KEY SIZE RECVED: {ksize}")
    vsize = get_size(data_to_write)
    handler_arr = [run_id, ksize, vsize, wfn_start_time, e_id, event_iter]

    # Putting object into required data store
    if ds == "s3":
        log_data = s3_put_handler(file_key, data_to_write, handler_arr)

    elif ds == "aurora":
        log_data = aurora_put_handler(file_key, data_to_write, handler_arr)

    elif ds == "dynamo":
        log_data = dynamo_put_handler(file_key, data_to_write, handler_arr)

    
    logger.info(json.dumps(log_data))

    return {
        'statusCode': 200,
        'body': 'Lambda executed successfully!'
    }

