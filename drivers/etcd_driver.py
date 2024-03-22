import boto3 


ec2 = boto3.client('ec2')

'''
Creating a VPC
'''
vpc_params = {
    'CidrBlock': '10.0.0.0/16',  
    'InstanceTenancy': 'default'  
}
try:
    response = ec2.create_vpc(**vpc_params)
    vpc_id = response['Vpc']['VpcId'] # Extract VPC ID
except Exception as e:
    print(f"ERROR: VPC creation failed")
    print(f"Error details: {str(e)}")


'''
Create security group for ec2
'''
security_group_params = {
    'Description': 'Open Security Group',
    'GroupName': 'OpenSecurityGroup',
    'VpcId': vpc_id
}

response = ec2.create_security_group(**security_group_params)
security_group_id = response['GroupId']

'''
Generate a key pair
'''
# 


# Create 3 EC2 instances for etcd nodes



# Create