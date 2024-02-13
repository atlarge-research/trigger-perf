import boto3
import json
import random

def invoker_function(key, data, r):
        client = boto3.client('lambda')
        payload = [key, data]
        
        response = client.invoke(
        FunctionName='send-lambda',
        InvocationType='Event',
        Payload=json.dumps(payload)
        )

def generate_rand_bytes(size):
    return str(bytes(random.choices(range(256), k=size)))

def lambda_handler(event, context):
    
    # Get w-k-r input
    jload = json.loads(event['body'])
    writes = jload.get('writes')
    keys = jload.get('keys')
    reads = jload.get('reads') # can add key & data size
    input = [writes, keys, reads]
    print(input)

    # Key and data generation
    for i in range(0,keys):
        key = generate_rand_bytes(10) # key size
        data = generate_rand_bytes(100) # data size

    # Invoke send/write function
    for i in range(0,keys): 
        invoker_function(key,data,reads)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

    # curl -X POST -H "Content-Type: application/json" -d '{"writes": "1", "keys": "n", "reads": "1"} https://jgtk3zdvy4.execute-api.eu-north-1.amazonaws.com/default/invoke-lambda