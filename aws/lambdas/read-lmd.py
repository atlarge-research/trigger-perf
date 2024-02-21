import time
import json
import boto3
import logger

def lambda_handler(event, context):

    ## After s3 trigger
    readfn_start_time = time.time()
    s3_event = event['Records'][0]['s3']
    bucket_name = s3_event['bucket']['name']
    object_key = s3_event['object']['key']
    ksize, vsize = 0, 0 # write logic to get sizes

    # Get the token from the S3 object metadata
    s3 = boto3.client('s3')
    response = s3.head_object(Bucket=bucket_name, Key=object_key)
    e_id = response['Metadata'].get('e_id')

    print(f"Lambda function triggered by S3 event")
    print(f"Bucket: {bucket_name}")
    print(f"Read start time: {readfn_start_time}")
    log_data = {
        'e_id': e_id,
        'event': 'TBE',
        'readfn_exec_start_time': readfn_start_time,
        'key': object_key,
        'key_size': ksize,
        'value_size': vsize
    }
    logger.info(json.dumps(log_data))

    return {
        'statusCode': 200,
        'body': 'Lambda executed successfully!',
        'lambda_execution_start_time': readfn_start_time
    }