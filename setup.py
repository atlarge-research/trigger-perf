from utils.utils import * 
from aws.aws import *
from drivers.s3_driver import *


def setup_services(acc_id): # Set up lambda functions & data store

    print("## Setup process started")
    # Setup Role ###TBD

    # Initial lambda setup
    create_lambda_function(acc_id, "initial-lmd")

    # Write lambda setup
    create_lambda_function(acc_id, "write-lmd")

    # Read lambda setup
    create_lambda_function(acc_id, "read-lmd")

    # Datastore setup
    create_s3_bucket("test-buck-xyz")
    s3_lambda_invoke_permission("read-lmd", "test-buck-xyz", acc_id)
    s3_lambda_event_notif_setup("read-lmd", "test-buck-xyz", acc_id)

    print("## Setup Complete!")
    pass

def main():
    test_configs = read_config('config.yaml')
    acc_id = test_configs['aws_acc_id']
    acc_id = 471112959817
    setup_services(acc_id)

    return

if __name__ == "__main__":

    main()