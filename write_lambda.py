import time
import boto3
import json

# need to enable versioning to gaurantee a notification for every event
def lambda_handler(event, context):

    # writing to s3
    recv_time = time.perf_counter()
    s3_event_time = event['Records'][0]['eventTime']
    
    s3_bucket = 'buczy-bucket'
    file_key = 'file-key5'
    data_to_write = {'key1': 'value1', 'key2': 'value2'}
    s3_client = boto3.client('s3')
    inv_time = time.perf_counter()
    s3_client.put_object(
        Bucket=s3_bucket,
        Key=file_key,
        Body=json.dumps(data_to_write),
        ContentType='application/json'
    )

    print(f"Data writen to S3")


    return {
        'statusCode': 200,
        'body': 'Lambda executed successfully!',
        'inv time': inv_time,
        's3_event_time': s3_event_time,
        'lambda_execution_time': recv_time
    }




