from aws.aws import run_command

def create_s3_bucket():
    bucket_name = "test-buck-xyz"
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


def delete_s3_bucket():
    pass

