import subprocess
import base64
import boto3
import time
import json


 ## id to be replaced


def run_command(cmd):
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        return  True, result.stdout.strip()
    except subprocess.CalledProcessError as err:
        print(f"Command failed: {cmd}, Error: {err}")
        return False, err.output
    
acc_id = 471112959817
fn_name = "testy"
def create_lambda_function(acc_id, fn_name):
    
    runtime = 'python3.8'
    handler = f"{fn_name}.lambda_handler"
    zip_file = f"fileb://aws/lambdas/{fn_name}.zip"
    role_arn = f"arn:aws:iam::{acc_id}:role/myLambdaRole"
    create_lambda_cmd = ['aws', 'lambda', 'create-function', \
                         '--function-name', fn_name, \
                         '--runtime', runtime, \
                         '--handler', handler, \
                         '--zip-file', zip_file, \
                         '--role', role_arn, \
                         '--logging-config', 'LogFormat=JSON' \
                        ]
    
    success, output = run_command(create_lambda_cmd)
    if success:
        print(f"-> Lambda function {fn_name} setup done")
    else:
        print(f"ERROR: Lambda function {fn_name} setup failed")
        print(output)
    return 0


'''
Used to Invoke the Initial lambda function
payload: {w-k-r}
'''
def lambda_invoke(fn_name, payload): # payload requires bas64 encoding
    enc_payload = base64.b64encode(payload.encode('utf-8')).decode('utf-8')
    
    lmd_invoke_cmd = [ 'aws', 'lambda', 'invoke', \
                      '--function-name', fn_name, \
                      '--invocation-type', 'Event', \
                    #   '--cli-binary-format', 'raw-in-base64-out', \
                      '--payload', enc_payload, \
                      '--region', 'eu-north-1', 'response.json' \
                    ]
    success, output = run_command(lmd_invoke_cmd)
    if success:
        print(f"Lambda function {fn_name} invoked")
        pass
    else:
        print(f"ERROR: Lambda function {fn_name} invocation failed")
    return 0




def get_lambda_logs(log_grp_name, start_time):

    cld_watch_logs = boto3.client('logs')
    all_results = []
    # Get all log streams within the specified log group
    log_streams_response = cld_watch_logs.describe_log_streams(
        logGroupName=log_grp_name,
        orderBy='LastEventTime',
        descending=True,
        limit=50 
    )
    for log_stream in log_streams_response['logStreams']:
        log_stream_name = log_stream['logStreamName']
        # Retrieve logs from CloudWatch Logs
        query = f'''
        fields @timestamp, @message
        | filter @timestamp >= {start_time}
        | filter @logStream = '{log_stream_name}'
        | filter @message like /TBE/
        '''
        query_results = cld_watch_logs.start_query(
            logGroupName=log_grp_name,
            startTime=int(start_time / 1000),  # Convert to seconds for CloudWatch Logs Insights
            endTime=int(time.time()),  # Current time
            queryString=query,
            limit=100  
        )
        # Retrieve the query ID
        query_id = query_results['queryId']
        print(query_id)
        while True: # poll to check if query is completed
            query_status = cld_watch_logs.get_query_results(queryId = query_id)
            print(query_status)
            if query_status == "Complete":
                break
            elif query_status == "Failed":
                print("ERROR: Query failed")
            print("sleeping")
            
            

        for result in query_status['results']:
            time_stamp = int(result[0]['value'])
            message = result[1]['value']
            # print(f"time_stamp: {time_stamp}, message: {message}")
            log_result = {
                'log_stream': log_stream_name,
                'timestamp': time_stamp,
                'message': message
            }
            all_results.append(log_result)

        print(json.dumps(all_results, indent=2))
        # if query_results['status'] == "Complete":
        #     for result in query_results['results']:
        #         timestamp = int(result[0]['value'])
        #         message = result[1]['value']
        #         print(f"Log Stream: {log_stream_name}, Timestamp: {timestamp}, Message: {message}")
        # else:
        #     print(f"Error executing query for log stream {log_stream_name}: {query_results.get('error_message')}")

        
        # print(query_results)
        break
    return 0


####################################
# def get_lambda_logs(log_grp_name, start_time):

#     cld_watch_logs = boto3.client('logs')

#     # Get all log streams within the specified log group
#     log_streams_response = cld_watch_logs.describe_log_streams(
#         logGroupName=log_grp_name,
#         orderBy='LastEventTime',
#         descending=True,
#         limit=50 
#     )
#     # print(log_streams_response)
#     for log_stream in log_streams_response['logStreams']:
#         log_stream_name = log_stream['logStreamName']
#         # Retrieve logs from CloudWatch Logs
#         response = cld_watch_logs.get_log_events(
#             logGroupName=log_grp_name,
#             logStreamName=log_stream_name,
#             startTime=start_time
#         )
#         print(response)
#         extract_from_logs(response)
#         break
#     return response


# def extract_from_logs(response): # exec start ts, ds put ts, Key, key size & val size
#     for event in response.get('events', []):
#             # Check if the log message contains "INFO"
#             if 'TBE' in event.get('message', ''):
#                 print(f"*** Extracted *** \n Log Timestamp: {event['timestamp']}, Message: {event['message']}")


if __name__ == "__main__":
    acc_id = 471112959817
    # fn_name = "write-lmd"
    # payload = '{"name": "Bob"}'
    # lambda_invoke(fn_name, payload)
    start_time = int((time.time() - 3600) * 1000)
    end_time = int(time.time() * 1000)
    log_group_name = '/aws/lambda/write-lmd'
    get_lambda_logs(log_group_name, start_time)