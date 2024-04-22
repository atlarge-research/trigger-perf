import boto3
import time


'''
Notes:
-----
-Has 3 instance types = Serverless v2, Memory-optimized, Burstable-classes
-Has 2 storage types = Standard, I/O optimized
-2 trigger options in Aurora: 1) native lambda sync/async function 2) Aurora->database activity streams->kinesis->lambda
-option 1 is not available in Aurora postgres
-Aurora MySql serverless v2 does not have API feature
-During Setup = Enable Public Access & RDS data API option, Disable automatic pause function
-DB cluster ID is not db name, default db name is postgres
-Aurora MySQL, Data API is only supported with Aurora Serverless v1
-Lambda function to be triggered should be within the same VPC as the db
-Choose postgres version that allows aws invoke calls


-Possible system configs for experiments
a) Mysql+memory optimized+Standard storage for native lambda trigger
b) Postgres+memory optimized+Standard storage for PL trigger
'''

# Create table with cols for keys & values
def aurora_create_table(cluster_arn, secret_arn, database_name, table_name, region='us-east-1'):
    client = boto3.client('rds-data', region_name=region)

    sql_statement = f"""
        CREATE TABLE {table_name} (
            id SERIAL PRIMARY KEY,
            key VARCHAR(255),
            value VARCHAR(255)
        )
    """
    try:
        resp = client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql=sql_statement
        )
        print("Table created successfully")
    except Exception as e:
        print(f"ERROR creating table: {e}")


def aurora_insert_data(cluster_arn, secret_arn, database_name, table_name, key, value, region='us-east-1'):
    client = boto3.client('rds-data', region_name=region)

    sql_statement = f"""
        INSERT INTO {table_name} (key, value)
        VALUES (:key, :value)
    """
    
    parameters = [
        {'name': 'key', 'value': {'stringValue': key}},
        {'name': 'value', 'value': {'stringValue': value}}
    ]
    
    try:
        resp = client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql=sql_statement,
            parameters=parameters
        )
        print("Data inserted successfully!")

    except Exception as e:
        print(f"ERROR inserting data: {e}")
    


def create_lambda_trigger(database_name, table_name, lambda_arn, region_name='us-east-1'):
    # Connect to AWS services
    rds_client = boto3.client('rds-data', region_name=region_name)

    # Define the trigger name
    trigger_name = f'trigger_lambda_{table_name}'

    # Create the trigger function in PL/pgSQL
    aws_extension_sql = """
    CREATE EXTENSION IF NOT EXISTS aws_lambda CASCADE;
    """
    function_sql = """
    CREATE OR REPLACE FUNCTION invoke_lambda()
    RETURNS TRIGGER AS $$
    BEGIN
        PERFORM aws_lambda.invoke(aws_commons.create_lambda_function_arn('arn:aws:lambda:us-east-1:133132736141:function:pg-recv', 'us-east-1'),
        json_build_object(
            'body', json_build_object(
                'message', 'Hello from Postgres!',
                'new_row', NEW
            )
        )::json);
        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;
    """ # need to replace lambda arn with f string

    # Create the trigger on the specified table
    trigger_sql = f"""
    CREATE TRIGGER {trigger_name}
    AFTER INSERT ON {table_name}
    FOR EACH ROW
    EXECUTE FUNCTION invoke_lambda();
    """
    sql_arr = []
    sql_arr.extend([aws_extension_sql, function_sql, trigger_sql])
    # Execute the SQL commands in the database
    try:
        response = rds_client.execute_statement(
            resourceArn="arn:aws:rds:us-east-1:133132736141:cluster:aurora-pg",
            secretArn="arn:aws:secretsmanager:us-east-1:133132736141:secret:rds!cluster-69e731ac-3d92-4bd0-8107-cff996d47a37-YRzaMp",
            database=database_name,
            sql=aws_extension_sql
        )
        response = rds_client.execute_statement(
            resourceArn="arn:aws:rds:us-east-1:133132736141:cluster:aurora-pg",
            secretArn="arn:aws:secretsmanager:us-east-1:133132736141:secret:rds!cluster-69e731ac-3d92-4bd0-8107-cff996d47a37-YRzaMp",
            database=database_name,
            sql=function_sql
        )
        response = rds_client.execute_statement(
            resourceArn="arn:aws:rds:us-east-1:133132736141:cluster:aurora-pg",
            secretArn="arn:aws:secretsmanager:us-east-1:133132736141:secret:rds!cluster-69e731ac-3d92-4bd0-8107-cff996d47a37-YRzaMp",
            database=database_name,
            sql=trigger_sql
        )
        print("Trigger setup complete!")
    except Exception as e:
        print("Error creating trigger:", e)

'''
Function to calculate simple latency of the pl trigger
'''
def aurora_latency_main_runner(cluster_arn, secret_arn, db_name, table_name, iters):
    
    for i in range(iters):
        send_time = time.time()
        aurora_insert_data(cluster_arn, secret_arn, db_name, table_name, f"{i}", f"{send_time}")
        time.sleep(1.5)


if __name__ == '__main__':
    cluster_arn = 'arn:aws:rds:us-east-1:133132736141:cluster:aurora-pg'
    secret_arn = 'arn:aws:secretsmanager:us-east-1:133132736141:secret:rds!cluster-69e731ac-3d92-4bd0-8107-cff996d47a37-YRzaMp'
    db_name = "postgres"
    table_name = 'kv_table'
    lambda_arn = 'arn:aws:lambda:us-east-1:133132736141:function:pg-recv'
    # create_lambda_trigger(db_name, table_name, lambda_arn, region_name='us-east-1')
    # aurora_create_table(cluster_arn, secret_arn, db_name, table_name)
    aurora_insert_data(cluster_arn, secret_arn, db_name, table_name, "test-key", "test-val")
    # aurora_latency_main_runner(cluster_arn, secret_arn, db_name, table_name, 3)



# DROP TRIGGER IF EXISTS trigger_lambda_kv_table ON kv_table;

## to get list of all triggers
# SELECT tgname AS trigger_name, relname AS table_name
# FROM pg_trigger
# JOIN pg_class ON (pg_class.oid = pg_trigger.tgrelid)
# ORDER BY table_name, trigger_name;

## to get list of all extensions
# SELECT * FROM pg_available_extensions;