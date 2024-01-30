import time

# need to enable versioning to gaurantee a notification for every event
def lambda_handler(event, context):
    recv_time = time.perf_counter()
    s3_event_time = event['Records'][0]['eventTime']
    
    # print(f"S3 event time: {s3_event_time}")
    # print(f"Receive time: {recv_time}")

    return {
        'statusCode': 200,
        'body': 'Lambda executed successfully!',
        's3_event_time': s3_event_time,
        'lambda_execution_time': recv_time
    }



