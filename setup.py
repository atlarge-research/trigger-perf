import utils.utils as utils
from aws.aws import *
from drivers.s3_driver import *


def setup_services(acc_id): # Set up lambda functions & data store

    print("## Setup process started")
    # Setup Role ###TBD

    # Initial lambda setup
    create_lambda_function(acc_id, "initial-lmd")

    # Write lambda setup
    create_lambda_function(acc_id, "write-lmd")

    # Datastore setup
    create_s3_bucket()

    # Read lambda setup
    create_lambda_function(acc_id, "read-lmd")

    print("## Setup Complete!")
    pass

def main():
    acc_id = 471112959817
    setup_services(acc_id)

    return

if __name__ == "__main__":

    main()