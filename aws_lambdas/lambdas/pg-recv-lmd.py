import json
import time
import logging

def aurora_recv_handler(recvfn_start_time, event_iter):
    log_data = {
        'run_id': "",
        'e_id': "",
        'event': 'RECV',
        'exec_start_time': recvfn_start_time,
        'put_time': 0,
        'key': str(event_iter),
        'key_size': '',
        'value_size': ''
    }
    return log_data

def lambda_handler(event, context):
    
    recvfn_start_time = time.time()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    print("Trigerred!")
    print(event)
    new_row = event['body']['new_row']
    event_iter = new_row['key']
    print(f"Event iter: {event_iter}")
    value = new_row['value']
    
    log_data = aurora_recv_handler(recvfn_start_time, event_iter)

    logger.info(json.dumps(log_data))
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
