import boto3




# Create Aurora Cluster
'''
Notes:
-----
-Has 3 instance type = Serverless v2, Memory-optimized, Burstable-classes
-Has 2 storage types = Standard, I/O optimized
-2 trigger options in Aurora: 1) native lambda sync/async function 2) Aurora->database activity streams->kinesis->lambda
-option 1 is not available in Aurora postgres
-During Setup = Enable Public Access & RDS data API option, Disable automatic pause function
-DB cluster ID is not db name, default db name is postgres
-Aurora MySql serverless v2 does not have API feature

-Possible system configs for experiments
a) Mysql + memory optimized for native lambda trigger
b) Postgres + serverless v2 for kinesis trigger
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
    

def setup_trigger_to_lambda_sync(cluster_arn, secret_arn, lambda_function_name, database_name, table_name, region='us-east-1'):
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
        print("Trigger created successfully")

    except Exception as e:
        print(f"Error setting up trigger for Lambda Sync Native function: {e}")




if __name__ == '__main__':
    cluster_arn = 'arn:aws:rds:us-east-1:133132736141:cluster:aurora-mysql'
    secret_arn = 'arn:aws:secretsmanager:us-east-1:133132736141:secret:rds!cluster-e79ac1af-3175-4ee8-9ba3-39272ba838ff-onxg54'
    db_name = "mysql"
    table_name = 'kv_table'
    aurora_create_table(cluster_arn, secret_arn, db_name, table_name)
    # aurora_insert_data(cluster_arn, secret_arn, db_name, table_name, "test-key", "test-val")