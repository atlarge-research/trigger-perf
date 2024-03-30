import time
import boto3
import json
import logging
from datetime import datetime

def lambda_handler(event, context):
    # TODO implement
    # writing to s3
    
    if 'Records' in event and len(event['Records']) > 0 and 'eventSource' in event['Records'][0] and event['Records'][0]['eventSource'] == 'aws:s3':
        # S3 event notification detected
        print("!@!@! Triggered by an S3 event")
        lmd_start_time = time.time()
        s3_event_time = event['Records'][0]['eventTime']
        datetime_object = datetime.strptime(s3_event_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        print(f"Lambda triggered at: {lmd_start_time}")
        print(f"S3 eventTime: {s3_event_time}")
        elp_time = lmd_start_time - datetime_object
        print(f"Elapsed time: {elp_time} ")
        print("Event:", json.dumps(event))
    else:
        # Not triggered by an S3 event
        print("Lambda was not triggered by an S3 event")
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        recv_time = time.time()
        logger.info(f"Write Lambda execution started at: {recv_time}")
        
        print(event)
        file_key = "file_key"
        data_to_write = "valval"
    
        s3_client = boto3.client('s3')
        s3_bucket = 'buczy-dest'
        
        s3_put_time = time.time()
        s3_put_datetime = datetime.now()
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=file_key,
            Body=json.dumps(data_to_write),
            ContentType='application/json'
        )
        logger.info(f"Write Lambda s3 put time: {s3_put_time}")
        logger.info(f"Write Lambda s3 put time: {s3_put_datetime}")
        print("## Event")
        print("Event:", event)
    
    
        print(f"Data writen to S3")
        print(f"lambda_execution_start_time: {recv_time}")
        print(f"s3_put_time: {s3_put_time}")
    
    
        return {
            'statusCode': 200,
            'body': 'Lambda executed successfully!',
            's3_put_time': s3_put_time,
            # 's3_event_time': s3_event_time,
            'lambda_execution_start_time': recv_time
        }