import time
import boto3
import json
import logging

# need to enable versioning to gaurantee a notification for every event
def lambda_handler(event, context):

    # writing to s3
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    recv_time = time.time()

    file_key = event[0]
    data_to_write = event[1]
    ksize = 0
    vsize = 0
    s3_client = boto3.client('s3')
    s3_bucket = 'test-buck-xyz'
    s3_put_time = time.time()
    s3_client.put_object(
        Bucket=s3_bucket,
        Key=file_key,
        Body=json.dumps(data_to_write),
        ContentType='application/json'
    )
    
    # TBE = to be extracted
    logger.info(f"TBE , Write Lambda execution started at: {recv_time}, \ 
                Write-lmd s3 put time: {s3_put_time}, Key: {file_key}, KeySize: {ksize}, ValSize: {vsize}")
    
    # print("Event:", event)
    # print(f"Data writen to S3")
    # print(f"lambda_execution_start_time: {recv_time}")
    # print(f"s3_put_time: {s3_put_time}")


    return {
        'statusCode': 200,
        'body': 'Lambda executed successfully!',
        's3_put_time': s3_put_time,
        # 's3_event_time': s3_event_time,
        'lambda_execution_start_time': recv_time
    }

# curl -X POST -H "Content-Type: application/json" -d '{"data": "key-val-pair", "writes": "value69", "keys": "value70"}' https://opw4dj08ul.execute-api.eu-north-1.amazonaws.com/default/send-lambda
