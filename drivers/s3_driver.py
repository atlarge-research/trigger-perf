import json 
import boto3
import time
import subprocess



def run_command(cmd):
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        return  True, result.stdout.strip()
    except subprocess.CalledProcessError as err:
        print(f"Error: {err}")
        return False, err.output


'''
Creates a bucket in us-east-1 region
'''

def create_s3_bucket(bucket_name, region='us-east-1'):
    region = 'us-east-1'  # change if needed

    s3_client = boto3.client('s3', region_name=region)

    try:
        # Create S3 bucket
        s3_client.create_bucket(
            Bucket=bucket_name
        )
        print(f"-> S3 bucket {bucket_name} setup done")
        return True
    except Exception as e:
        print(f"ERROR: S3 bucket {bucket_name} setup failed. {str(e)}")
        return False



'''
Grants Lambda permission to be invoked by a S3 bucket:- for 'read-lmd' only
'''
# def s3_lambda_invoke_permission(fn_name, bucket_name, acc_id):
#     arn = f"arn:aws:s3:::{bucket_name}"
#     s3_lambda_invoke_permission_cmd = [ 'aws', 'lambda', 'add-permission', \
#                                         '--function-name', fn_name, \
#                                         '--principal', 's3.amazonaws.com', \
#                                         '--statement-id', 's3invoke', \
#                                         '--action', 'lambda:InvokeFunction', \
#                                         '--source-arn', arn, \
#                                         '--source-account', str(acc_id) \
#                                     ]
#     success, output = run_command(s3_lambda_invoke_permission_cmd)
#     if success:
#         print(f"-> S3-Lambda (read-lmd) permissions set up")
#     else:
#         print(f"ERROR: S3-Lambda (read-lmd) permission setup failed")
    
#     return 0

def s3_lambda_invoke_permission(fn_name, bucket_name, acc_id, region='us-east-1'):
    lambda_client = boto3.client('lambda', region_name=region)

    try:
        arn = f"arn:aws:s3:::{bucket_name}"
        lambda_client.add_permission(
            FunctionName=fn_name,
            StatementId='s3invoke',
            Action='lambda:InvokeFunction',
            Principal='s3.amazonaws.com',
            SourceArn=arn,
            SourceAccount=str(acc_id)
        )
        print("-> S3-Lambda (read-lmd) permissions set up")
        return True
    except Exception as e:
        print(f"ERROR: S3-Lambda (read-lmd) permission setup failed: {str(e)}")
        return False
    

'''
Sets up S3 bucket Event notification to trigger 'read-lmd'
'''
def s3_lambda_event_notif_setup(fn_name, bucket_name, acc_id):

    notif_config = f'''
                        {{
                        "LambdaFunctionConfigurations": [
                            {{
                            "LambdaFunctionArn": "arn:aws:lambda:us-east-1:{acc_id}:function:{fn_name}",
                            "Events": ["s3:ObjectCreated:*"]
                            }}                                 
                        ]
                        }}
                    '''
    
    s3_lambda_event_notif_setup_cmd = [ 'aws', 's3api', 'put-bucket-notification-configuration', \
                                        '--bucket', bucket_name, \
                                        '--notification-configuration', notif_config \
                                        ]
    success, output = run_command(s3_lambda_event_notif_setup_cmd)
    if success:
        print(f"-> S3-read-lmd Event notification set up")
    else:
        print(f"ERROR: S3-read-lmd Event notification failed")
    
    return 0

def s3_put_object(file_key, data):
    s3_client = boto3.client('s3')
    s3_bucket = 'test-buck-xyz'
    metadata = {'e_id': str(0)} # Remove later
    put_time = time.time()
    resp = s3_client.put_object(
        Bucket=s3_bucket,
        Key=file_key,
        Body=json.dumps(data),
        Metadata=metadata,
        ContentType='application/json'
    )
    xar_id = resp['ResponseMetadata']['HTTPHeaders']['x-amz-request-id']
    return xar_id, put_time


def delete_s3_bucket():
    pass

