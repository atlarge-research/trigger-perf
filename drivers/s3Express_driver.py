import logging
from botocore.exceptions import ClientError

import boto3

def create_s3Express_bucket(bucket_name, availability_zone='use1-az4', region='us-east-1'):

    s3_client = boto3.client('s3', region_name=region)
    try:
        bucket_config = {
                'Location': {
                    'Type': 'AvailabilityZone',
                    'Name': availability_zone
                },
                'Bucket': {
                    'Type': 'Directory', 
                    'DataRedundancy': 'SingleAvailabilityZone'
                }
            }
        response = s3_client.create_bucket(
            # ACL='public-read-write',
            Bucket=bucket_name,
            CreateBucketConfiguration=bucket_config
        )
        print(f"-> S3 Express directory bucket '{bucket_name}' setup done")
        return True
    except Exception as e:
        print(f"ERROR: S3 Express directory bucket '{bucket_name}' setup failed. {str(e)}")
        return False



if __name__ == '__main__':
    bucket_name = 'ritul-buck--use1-az4--x-s3'
    region = 'us-east-1'
    availability_zone = 'use1-az4'
    create_s3Express_bucket(bucket_name, availability_zone, region)