import time
import json


def lambda_handler(event, context):

    ## After s3 trigger
    start_time = time.perf_counter()
    s3_event = event['Records'][0]['s3']
    bucket_name = s3_event['bucket']['name']
    object_key = s3_event['object']['key']
    
    print(f"Lambda function triggered by S3 event")
    print(f"Bucket: {bucket_name}")

    return {
        'statusCode': 200,
        'body': 'Lambda executed successfully!',
        # 'inv time': inv_time,
        # 's3_event_time': s3_event_time,
        'lambda_execution_start_time': start_time
    }