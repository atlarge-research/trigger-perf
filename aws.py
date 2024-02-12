import subprocess



 ## id to be replaced


def run_command(cmd):
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        return  True, result.stdout.strip()
    except subprocess.CalledProcessError as err:
        print(f"Command failed: {cmd}, Error: {err}")
        return False, None
    
acc_id = 471112959817
fn_name = "testy"
def create_lambda_function(acc_id, fn_name):
    
    runtime = 'python3.8'
    handler = f"{fn_name}.lambda_handler"
    zip_file = f"fileb://{fn_name}.zip"
    role_arn = f"arn:aws:iam::{acc_id}:role/myLambdaRole"
    create_lambda_cmd = ['aws', 'lambda', 'create-function', \
                         '--function-name', fn_name, \
                         '--runtime', runtime, \
                         '--handler', handler, \
                         '--zip-file', zip_file, \
                         '--role', role_arn \
                        ]
    
    success, output = run_command(create_lambda_cmd)
    if success:
        print(f"-> Lambda function {fn_name} setup done")
    else:
        print(f"ERROR: Lambda function {fn_name} setup failed")
    
    return 0


# if __name__ == "__main__":
#     acc_id = 471112959817
#     fn_name = "testy"
#     create_lambda_function(acc_id, fn_name)