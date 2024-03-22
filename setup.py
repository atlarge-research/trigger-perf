from utils.utils import * 
from aws.aws import *
from drivers.s3_driver import *
from drivers.dynamo_driver import *


def setup_services(acc_id, ds): # Set up lambda functions & data store

    print("## Setup process started")

    # Setup Role ###TBD
    # create_aws_role('myLambdaRole')
    # time.sleep(7)

    # Initial lambda setup
    create_lambda_function(acc_id, "initial-lmd")

    # Write lambda setup
    create_lambda_function(acc_id, "write-lmd")

    # Read lambda setup
    create_lambda_function(acc_id, "read-lmd")

    # Datastore setup
    if ds == "s3":
        create_s3_bucket("test-buck-ritul")
        s3_lambda_invoke_permission("read-lmd", "test-buck-ritul", acc_id)
        s3_lambda_event_notif_setup("read-lmd", "test-buck-ritul", acc_id)
    elif ds == "s3Express":
        
        pass
    elif ds == "dynamo":
        create_dynamo_table("trigger-perf")
        dynamo_lambda_streams_setup("trigger-perf", "read-lmd", acc_id)
    elif ds == "etcd":
        pass

    print(f"## {ds} Setup Complete!")
    pass

def main():
    test_configs = read_config('config.yaml')
    acc_id = test_configs['aws_acc_id']
    ds = test_configs['data_store']
    
    setup_services(acc_id, ds)
    # create_aws_role('myLambdaRole')
    

    return

if __name__ == "__main__":
    main()