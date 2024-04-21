import boto3
import mysql.connector


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
b) Postgres+memory optimized+Standard storage for kinesis trigger
'''

# Create Aurora Cluster
def aurora_create_db():
    pass



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
    

def aurora_setup_nativefn_lambda_sync(cluster_arn, secret_arn, lambda_function_name, database_name, table_name, region='us-east-1'):
    rds_data_client = boto3.client('rds-data', region_name=region)

    # Create a stored procedure to call the Lambda function synchronously
    create_nativefn_proc_sql = f"""
        CREATE PROCEDURE InvokeLambdaOnInsert()
        BEGIN
            DECLARE lambda_response JSON;
            SET lambda_response = mysql.lambda_sync(
                '{lambda_function_name}',
                '{{
                    "key": "value"
                }}'
            );
        END
    """

    # Create a trigger to invoke the stored procedure upon insert into the table
    create_trigger_sql = f"""
        CREATE TRIGGER TriggerLambdaOnInsert
        AFTER INSERT ON {table_name}
        FOR EACH ROW
        CALL InvokeLambdaOnInsert()
    """

    try:
        # Execute the SQL statements to create stored procedure and trigger
        rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql=create_nativefn_proc_sql
        )
        print("Sync Native function stored procedure created successfully!")
    except Exception as e:
        print(f"Error setting up Sync Native function stored procedure: {e}")

    try:

        rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql=create_trigger_sql
        )
        print("Trigger created successfully!")

    except Exception as e:
        print(f"Error setting up trigger for Lambda Sync Native function: {e}")

def aurora_setup_nativefn_lambda_sync():
    pass

def mysql_connector():
    aurora_host = 'aurora-ms-instance-1.cclvbbfkpkke.us-east-1.rds.amazonaws.com'
    aurora_user = 'mysql'
    aurora_password = 'mysqlrooty'
    aurora_database = 'aurora-ms'
    try:
        print("connecting....")
        connection = mysql.connector.connect(
            host=aurora_host,
            user=aurora_user,
            password=aurora_password,
            database=aurora_database
        )
        cursor = connection.cursor()
        print(f"Connection Successful!")
        return cursor
    except Exception as e:
        print(f"Error connecting to mysql: {e}")


def create_lambda_trigger(database_name, table_name, lambda_arn, region_name='us-east-1'):
    # Connect to AWS services
    rds_client = boto3.client('rds-data', region_name=region_name)
    lambda_client = boto3.client('lambda', region_name=region_name)

    # Define the trigger name
    trigger_name = f'trigger_{database_name}_{table_name}'

    # Create the trigger function in PL/pgSQL

    aws_extension_sql = """
    CREATE EXTENSION IF NOT EXISTS aws_lambda CASCADE;
    """
    function_sql = """
    CREATE OR REPLACE FUNCTION invoke_lambda()
    RETURNS TRIGGER AS $$
    BEGIN
        PERFORM aws_lambda.invoke('arn:aws:lambda:us-east-1:133132736141:function:rds-recv', '{"message": "Trigger fired"}'::json);
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """ # need to replace lambda arn with f string
#PERFORM aws_lambda.invoke('arn:aws:lambda:us-east-1:133132736141:function:rds-recv', '{{"message": "Trigger fired"}}'::json);
#SELECT * from aws_lambda.invoke(aws_commons.create_lambda_function_arn('arn:aws:lambda:us-east-1:133132736141:function:rds-recv', 'us-east-1'), '{"body": "Hello from Postgres!"}'::json );
    # Create the trigger on the specified table
    trigger_sql = f"""
    CREATE TRIGGER {trigger_name}
    AFTER INSERT OR UPDATE OR DELETE ON {table_name}
    FOR EACH ROW
    EXECUTE FUNCTION invoke_lambda();
    """
    sql_arr = []
    sql_arr.extend([aws_extension_sql, function_sql, trigger_sql])
    # Execute the SQL commands in the database
    try:
        response = rds_client.execute_statement(
            resourceArn="arn:aws:rds:us-east-1:133132736141:cluster:aurora-pg",
            secretArn="arn:aws:secretsmanager:us-east-1:133132736141:secret:rds!cluster-4817e0a8-b3e5-4f2e-9cb5-f1eab2d23b2c-gsetgj",
            database=database_name,
            sql=function_sql
        )
        # for i in range(len(sql_arr)):
        #     response = rds_client.execute_statement(
        #         resourceArn="arn:aws:rds:us-east-1:133132736141:cluster:aurora-pg",
        #         secretArn="arn:aws:secretsmanager:us-east-1:133132736141:secret:rds!cluster-4817e0a8-b3e5-4f2e-9cb5-f1eab2d23b2c-gsetgj",
        #         database=database_name,
        #         sql=sql_arr[i]
        #     )
        # if i == 0:
        #     print("Lambda extension installed successfully!")
        # elif i == 1:
        #     print("Function created successfully!")
        # elif i == 2:
        #     print("Trigger created successfully!")

    except Exception as e:
        print("Error creating trigger:", e)

    # Add Lambda invocation permission to the trigger function
    # try:
    #     lambda_client.add_permission(
    #         FunctionName=lambda_function_arn.split(':')[-1],
    #         StatementId='lambda-trigger-permission',
    #         Action='lambda:InvokeFunction',
    #         Principal='rds.amazonaws.com',
    #         SourceArn="arn:aws:rds:us-east-1:133132736141:cluster:aurora-pg"
    #     )
    #     print("Lambda invocation permission added successfully!")
    # except Exception as e:
    #     print("Error adding Lambda invocation permission:", e)





if __name__ == '__main__':
    cluster_arn = 'arn:aws:rds:us-east-1:133132736141:cluster:aurora-pg'
    secret_arn = 'arn:aws:secretsmanager:us-east-1:133132736141:secret:rds!cluster-4817e0a8-b3e5-4f2e-9cb5-f1eab2d23b2c-gsetgj'
    db_name = "postgres"
    table_name = 'kv_table'
    lambda_arn = 'arn:aws:lambda:us-east-1:133132736141:function:rds-recv'
    # create_lambda_trigger(db_name, table_name, lambda_arn, region_name='us-east-1')

    
    # cur = mysql_connector()
    # aurora_create_table(cluster_arn, secret_arn, db_name, table_name)
    aurora_insert_data(cluster_arn, secret_arn, db_name, table_name, "test-key", "test-val")