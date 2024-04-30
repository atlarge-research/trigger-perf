import boto3

'''
Creates a dynamodb table, default region = us-east-1
'''
def create_dynamo_table(table_name: str, region='us-east-1'):
    dynamo = boto3.client('dynamodb', region_name='us-east-1')
    table_name = "trigger-perf"
    resp = dynamo.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'id', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        },
        StreamSpecification={
            'StreamEnabled': True,
            'StreamViewType': 'NEW_IMAGE'  # To change
        }
    )
    print(f"-> Creating Dynamo table '{table_name}'....")
    resp_w = dynamo.get_waiter('table_exists').wait(TableName=table_name)
    print("-> Created table")

    return 0

def add_dynamo_permissions():
    pass


def dynamo_lambda_streams_setup(table_name: str, fn_name: str, acc_id):

    dynamo = boto3.client('dynamodb', region_name='us-east-1')
    response = dynamo.describe_table(TableName=table_name)
  
    stream_arn = response['Table']['LatestStreamArn']
    print(f"STREAM_ARN: {stream_arn}")

    try: 
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        lmd_fn_arn = f"arn:aws:lambda:us-east-1:{acc_id}:function:{fn_name}"
        resp = lambda_client.create_event_source_mapping(
            EventSourceArn=stream_arn,
            FunctionName=lmd_fn_arn,
            Enabled=True,
            StartingPosition='TRIM_HORIZON'
        )
    except Exception as e:
        print(f"ERROR: Lambda streams event source mapping setup failed. {str(e)}")
        print(resp)



def dynamo_put_item(table_name, key, value, region='us-east-1'):
    dynamodb = boto3.client('dynamodb', region_name=region)
    item = {
    'id': {'S': key},     
    'value': {'S': value}  
    }

    try:
        resp = dynamodb.put_item(
            TableName=table_name,
            Item=item
        )
    except Exception as e:
        print(f"ERROR: Failed to insert kv pair to dynamo, {str(e)}")
    print(resp)
    return resp


# dynamo_lambda_streams_setup("trigger-perf", "read-lmd", acc_id=133132736141)
# dynamo_put_item("trigger-perf", "gyz", "123")