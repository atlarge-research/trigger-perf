import subprocess
import base64


 ## id to be replaced


def run_command(cmd):
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        return  True, result.stdout.strip()
    except subprocess.CalledProcessError as err:
        print(f"Command failed: {cmd}, Error: {err}")
        return False, err.output
    
acc_id = 471112959817
fn_name = "testy"
def create_lambda_function(acc_id, fn_name):
    
    runtime = 'python3.8'
    handler = f"{fn_name}.lambda_handler"
    zip_file = f"fileb://aws/lambdas/{fn_name}.zip"
    role_arn = f"arn:aws:iam::{acc_id}:role/myLambdaRole"
    create_lambda_cmd = ['aws', 'lambda', 'create-function', \
                         '--function-name', fn_name, \
                         '--runtime', runtime, \
                         '--handler', handler, \
                         '--zip-file', zip_file, \
                         '--role', role_arn, \
                         '--logging-config', 'LogFormat=JSON' \
                        ]
    
    success, output = run_command(create_lambda_cmd)
    if success:
        print(f"-> Lambda function {fn_name} setup done")
    else:
        print(f"ERROR: Lambda function {fn_name} setup failed")
        print(output)
    return 0


'''
Used to Invoke the Initial lambda function
payload: {w-k-r}
'''
def lambda_invoke(fn_name, payload): # payload requires bas64 encoding
    enc_payload = base64.b64encode(payload.encode('utf-8')).decode('utf-8')
    
    lmd_invoke_cmd = [ 'aws', 'lambda', 'invoke', \
                      '--function-name', fn_name, \
                      '--invocation-type', 'Event', \
                    #   '--cli-binary-format', 'raw-in-base64-out', \
                      '--payload', enc_payload, \
                      '--region', 'eu-north-1', 'response.json' \
                    ]
    success, output = run_command(lmd_invoke_cmd)
    if success:
        print(f"Lambda function {fn_name} invoked")
        pass
    else:
        print(f"ERROR: Lambda function {fn_name} invocation failed")
    return 0


# if __name__ == "__main__":
#     acc_id = 471112959817
#     fn_name = "write-lmd"
#     payload = '{"name": "Bob"}'
#     lambda_invoke(fn_name, payload)