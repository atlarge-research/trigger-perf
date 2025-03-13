from utils.utils import * 
from drivers.aws import *
from drivers.s3_driver import *
from drivers.dynamo_driver import *
from drivers.s3Express_driver import *


def setup_services(acc_id, ds, region): # Set up lambda functions & data store

    print("## Setup process started")

    # Setup Role ###TBD
    # create_aws_lambda_role('myLambdaRole')
    # time.sleep(7)

    #Initial lambda setup
    create_lambda_function(acc_id, "initial-lmd")

    # Write lambda setup
    create_lambda_function(acc_id, "write-lmd")

    # Read lambda setup
    create_lambda_function(acc_id, "read-lmd")

    # Datastore setup
    try:
        if ds == "s3":
            statement_id = 's3invoke'
            # create_s3_bucket("test-buck-ritul")
            s3_lambda_invoke_permission("read-lmd", "test-buck-ritul", acc_id, statement_id, region)
            s3_lambda_event_notif_setup("read-lmd", "test-buck-ritul", acc_id, region)

        elif ds == "s3Express":
            availability_zone= 'use1-az4' # change if needed
            statement_id = 's3Expressinvoke'
            create_s3Express_bucket("ritul-express--use1-az4--x-s3", availability_zone, region)
            s3_lambda_invoke_permission("read-lmd", "ritul-express--use1-az4--x-s3", acc_id, statement_id, region)
            s3_lambda_event_notif_setup("read-lmd", "ritul-express--use1-az4--x-s3", acc_id, region)
            
        elif ds == "dynamo":
            create_dynamo_table("trigger-perf")
            dynamo_lambda_streams_setup("trigger-perf", "read-lmd", acc_id)

        elif ds == "aurora":
            pass

        print(f"## {ds} Setup Complete!")
    except Exception as e:
        print(f"{ds} setup failed with error: {e}")


def main():
    test_configs = read_config('config.yaml')
    acc_id = test_configs['aws_acc_id']
    ds = test_configs['data_store']
    region = test_configs['region'] # send region to funcs
    
    setup_services(acc_id, ds, region)
    # create_aws_lambda_role('myLambdaRole', 'us-east-1')

    ## EC2 setup check
    # create_aws_ec2_role('myEC2Role', 'us-east-1')
    # role_arn = 'arn:aws:iam::133132736141:role/myEC2Role'
    # inst_prof_arn = 'arn:aws:iam::133132736141:instance-profile/myEC2Role'
    # attach_role_to_ec2('i-0580939aecc5dd41b', 'myEC2Role', inst_prof_arn)
    

    return

if __name__ == "__main__":
    main()