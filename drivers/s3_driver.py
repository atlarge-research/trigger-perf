import json 

from aws.aws import run_command


'''
Creates a bucket in eu-north-1 region
'''
def create_s3_bucket(bucket_name):
    # bucket_name = "test-buck-xyz"
    # aws s3api create-bucket \
    # --bucket test-buckxyz \
    # --create-bucket-configuration LocationConstraint=eu-north-1
    create_s3bucket_cmd = [
        'aws', 's3api', 'create-bucket', \
        '--bucket', bucket_name, \
        '--create-bucket-configuration', \
        'LocationConstraint=eu-north-1' 
    ]
    success, output = run_command(create_s3bucket_cmd)
    if success:
        print(f"-> S3 bucket {bucket_name} setup done")
    else:
        print(f"ERROR: S3 bucket {bucket_name} setup failed")

    return 0



'''
Grants Lambda permission to be invoked by a S3 bucket:- for 'read-lmd' only
'''
def s3_lambda_invoke_permission(fn_name, bucket_name, acc_id):
    arn = f"arn:aws:s3:::{bucket_name}"
    s3_lambda_invoke_permission_cmd = [ 'aws', 'lambda', 'add-permission', \
                                        '--function-name', fn_name, \
                                        '--principal', 's3.amazonaws.com', \
                                        '--statement-id', 's3invoke', \
                                        '--action', 'lambda:InvokeFunction', \
                                        '--source-arn', arn, \
                                        '--source-account', str(acc_id) \
                                    ]
    success, output = run_command(s3_lambda_invoke_permission_cmd)
    if success:
        print(f"-> S3-Lambda (read-lmd) permissions set up")
    else:
        print(f"ERROR: S3-Lambda (read-lmd) permission setup failed")
    
    return 0


'''
Sets up S3 bucket Event notification to trigger 'read-lmd'
'''
def s3_lambda_event_notif_setup(fn_name, bucket_name, acc_id):

    notif_config = f'''
                        {{
                        "LambdaFunctionConfigurations": [
                            {{
                            "LambdaFunctionArn": "arn:aws:lambda:eu-north-1:{acc_id}:function:{fn_name}",
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


def delete_s3_bucket():
    pass

