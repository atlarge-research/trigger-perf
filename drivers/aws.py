import subprocess
import base64
import boto3
import time
import json
import csv
import zipfile


ec2 = boto3.client('ec2', region_name='us-east-1')

## id to be replaced
def run_command(cmd):
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        return  True, result.stdout.strip()
    except subprocess.CalledProcessError as err:
        print(f"Error: {err}")
        return False, err.output

'''
Creates an aws role that grants full permission
for Lambda, S3 and Dynamo.
role_name = 'myLambdaRole'
'''
def create_aws_lambda_role(role_name, region):

    aws_client = boto3.client('iam', region_name=region)

    lambda_assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    # Create IAM role for Lambda execution
    role_response = aws_client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(lambda_assume_role_policy)
    )

    # Grants s3 & dynamo full access
    policies_to_attach = [
        'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
        'arn:aws:iam::aws:policy/AmazonS3FullAccess',
        'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess',
        'arn:aws:iam::aws:policy/CloudWatchFullAccess',
        'arn:aws:iam::aws:policy/AWSLambda_FullAccess',
        'arn:aws:iam::aws:policy/AWSLambdaInvocation-DynamoDB',
        'arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess',
    ]
    # Attaching the policies to the role
    for pol in policies_to_attach:
        aws_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=pol
        )

    role_arn = role_response['Role']['Arn']
    print(f"AWS Lambda role created, Execution Role ARN: {role_arn}")
    return role_arn


'''
Create AWS EC2 role with full permissions,
Also creates a instance profile and attaches role to it.
Role name is used for the inst_prof name as well.
role_name = 'myEC2Role'
return: role_arn, inst_prof_arn
'''
def create_aws_ec2_role(role_name, region):
    
    iam = boto3.client('iam', region_name=region)

    policy_doc = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "ec2.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    try: 
        role_resp = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(policy_doc)
        )
        policies_to_attach = [
            'arn:aws:iam::aws:policy/AmazonEC2FullAccess',
            'arn:aws:iam::aws:policy/AmazonSSMFullAccess',
            'arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore',
            'arn:aws:iam::aws:policy/AmazonSSMManagedEC2InstanceDefaultPolicy'
        ]
        # Attaching the policies to the role
        for pol in policies_to_attach:
            iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn=pol
            )
        role_arn = role_resp['Role']['Arn']

        inst_profile_resp = iam.create_instance_profile(
            InstanceProfileName=role_name
        )
        inst_profile_arn = inst_profile_resp['InstanceProfile']['Arn']

        # add role to instance profile
        resp = iam.add_role_to_instance_profile(
            InstanceProfileName=role_name,
            RoleName=role_name
        )
    
        print(role_arn)
        print(inst_profile_arn)
        return role_arn, inst_profile_arn
    
    
    except Exception as e:
        print(f"ERROR: EC2 Role setup failed")
        print(f"Error details: {str(e)}")
        return None

'''
Attaches Role to given ec2 instance
args: ec2 instance id, role name, instance profile arn 
'''
def attach_role_to_ec2(inst_id, role_name, inst_prof_arn):
    try:
        resp = ec2.associate_iam_instance_profile(
            IamInstanceProfile={
                'Arn': inst_prof_arn,
                'Name': role_name
            },
            InstanceId=inst_id
        )
    except Exception as e:
        print(f"ERROR: attaching role to EC2 instances failed")
        print(f"Error details: {str(e)}")
        return None


# def create_lambda_function(acc_id, fn_name):
    
#     runtime = 'python3.8'
#     handler = f"{fn_name}.lambda_handler"
#     zip_file = f"fileb://aws/lambdas/{fn_name}.zip"
#     role_arn = f"arn:aws:iam::{acc_id}:role/myLambdaRole"
# create_lambda_cmd = ['aws', 'lambda', 'create-function', \
#                      '--function-name', fn_name, \
#                      '--runtime', runtime, \
#                      '--handler', handler, \
#                      '--zip-file', zip_file, \
#                      '--role', role_arn, \
#                      '--logging-config', 'LogFormat=JSON' \
#                     ]

#     success, output = run_command(create_lambda_cmd)
#     if success:
#         print(f"-> Lambda function {fn_name} setup done")
#     else:
#         print(f"ERROR: Lambda function {fn_name} setup failed")
#         print(output)
#     return 0

def create_lambda_function(acc_id, fn_name):
    lambda_client = boto3.client('lambda', region_name='us-east-1')  # Replace with your desired region
    
    # Upload Lambda function code (ZIP file)
    with zipfile.ZipFile(f'./aws_lambdas/lambdas/{fn_name}.zip', 'w') as zip_file:
        # Add your Lambda function files to the ZIP file
        zip_file.write(f'./aws_lambdas/lambdas/{fn_name}.py', arcname=f'{fn_name}.py')

    with open(f'./aws_lambdas/lambdas/{fn_name}.zip', 'rb') as code_file:
        function_code = code_file.read()

    # Create or update Lambda function
    try:
        response = lambda_client.create_function(
            FunctionName=fn_name,
            Runtime='python3.8',
            Handler=f'{fn_name}.lambda_handler',
            Role=f'arn:aws:iam::{acc_id}:role/myLambdaRole',
            Code={'ZipFile': function_code},
            LoggingConfig={'LogFormat': 'JSON'},
        )
        print(f"-> Lambda function {fn_name} setup done")
        return response
    except Exception as e:
        print(f"ERROR: Lambda function {fn_name} setup failed")
        print(f"Error details: {str(e)}")
        return None




'''
Used to Invoke the Initial lambda function
'''
def lambda_invoke(fn_name, payload): # payload requires bas64 encoding
    
    if isinstance(payload, dict):
        payload = json.dumps(payload)

    enc_payload = base64.b64encode(payload.encode('utf-8')).decode('utf-8')
    
    lmd_invoke_cmd = [ 'aws', 'lambda', 'invoke', \
                      '--function-name', fn_name, \
                      '--invocation-type', 'Event', \
                    #   '--cli-binary-format', 'raw-in-base64-out', \
                      '--payload', enc_payload, \
                      '--region', 'us-east-1', 'response.json' \
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
def write_to_csv(output_file_path, logs, delimiter=','):
    with open(output_file_path, mode='w', newline='') as csv_file:
        fieldnames = logs[0].keys() if logs else []
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(logs)
       

'''
Get all lambda function logs for the given timestamp
'''
def get_lambda_logs(lmd_fn, start_time, run_id):
    region = 'us-east-1'
    cld_watch_logs = boto3.client('logs', region_name=region)
    log_grp_name = f"/aws/lambda/{lmd_fn}"

    try:
        # Verify the existence of the log group
        cld_watch_logs.describe_log_groups(logGroupNamePrefix=log_grp_name)
    except cld_watch_logs.exceptions.ResourceNotFoundException:
        print(f"Log group '{log_grp_name}' does not exist.")
        return []
    
    res_logs = []

    # Query to get all logs after timestamp from log group
    query = f'''
    fields @timestamp, @message
    | filter @message like /run_id/
    | sort @timestamp desc
    '''

    # print(f"START_TIME: {start_time}\n")
    query_results = cld_watch_logs.start_query(
        logGroupName=log_grp_name,
        startTime=int(start_time/1000),  # Convert to seconds for CloudWatch Logs Insights
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
    # print(res_logs)
    # print(f"{lmd_fn} logs extracted")
    print(res_logs)
    write_to_csv(f"logs/{lmd_fn}_logs.csv", res_logs, delimiter=',')
    # print(res_logs)
    return res_logs

def logs_master(lmd_fn, start_time, run_id):
    
    max_retries = 3
    total_events = 30
    for _ in range(max_retries):
        logs = get_lambda_logs(lmd_fn, start_time, run_id)

        if logs != None:
            ctr = 0
            for log in logs:
                if log['run_id'] == run_id:
                    ctr += 1
            if ctr >= total_events:
                return("All event logs received!")
            else:
                print(f"Only {ctr}/{total_events} received. Retrying in 30 secs...")
        time.sleep(30)
        print("getting logs...")


if __name__ == "__main__":
    acc_id = 133132736141
    # create_aws_role('myLambdaRole')
    role_arn = create_aws_ec2_role('myEC2Role', 'us-east-1')
    # attach_role_to_ec2('i-0df18bbee26fcf028', role_arn)
    
    


