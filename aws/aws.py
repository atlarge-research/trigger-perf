import subprocess
import base64
import boto3
import time
import json
import csv


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


'''
Creates & writes to a csv file 
'''
def write_to_csv(output_file_path, logs):
    with open(output_file_path, mode='w', newline='') as csv_file:
        fieldnames = logs[0].keys() if logs else []
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(logs)
       

'''
Get all lambda function logs for the given timestamp
'''
def get_lambda_logs(lmd_fn, start_time):

    cld_watch_logs = boto3.client('logs')
    log_grp_name = f"/aws/lambda/{lmd_fn}"
    res_logs = []
    # Get all log streams within the specified log group
    log_streams_response = cld_watch_logs.describe_log_streams(
        logGroupName=log_grp_name,
        orderBy='LastEventTime',
        descending=True,
        limit=50 
    )
    # Query to get all logs after timestamp from log group
    query = f'''
    fields @timestamp, @message
    | filter @timestamp >= {start_time}
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
    while True: # poll to check if query is completed
        query_status = cld_watch_logs.get_query_results(queryId = query_id)
        # print(f"Query Status: {query_status}\n")
        if query_status['status'] == "Complete":
            break
        elif query_status['status'] == "Failed":
            print("ERROR: Query failed")
            break
        # print("sleeping....")
        time.sleep(1)
        
    for result in query_status.get('results',[]):
        # print("RESULT\n")
        log_value = result[1]['value']
        lv_json = json.loads(log_value)
        message = lv_json['message']
        msg_json = json.loads(message)
        res_logs.append(msg_json)

    write_to_csv(f"../logs/{lmd_fn}_logs.csv", res_logs)
    return res_logs


if __name__ == "__main__":
    acc_id = 471112959817
    # fn_name = "write-lmd"
    # payload = '{"name": "Bob"}'
    # lambda_invoke(fn_name, payload)
    start_time = int((time.time() - 3600) * 1000)
    end_time = int(time.time() * 1000)
    lmd_fn = "write-lmd"
    get_lambda_logs(lmd_fn, start_time)


# query = f'''
# fields @timestamp, @message
# | filter @timestamp >= {start_time}
# | filter @logStream = '{log_stream_name}'
# | filter @message like /TBE/
# '''