import boto3 


ec2 = boto3.client('ec2', region_name='us-east-1')

'''
Creating a VPC
return: vpc id, subnet id
'''
def create_vpc():
    vpc_params = {
        'CidrBlock': '172.31.0.0/16',  
        'InstanceTenancy': 'default'    
    }
    try:
        response = ec2.create_vpc(**vpc_params)
        vpc_id = response['Vpc']['VpcId'] # Extract VPC ID
        print(vpc_id)
        # Create Subnet
        subnet_params = {
            'CidrBlock': '172.31.0.0/24',  # Subnet within the VPC range
            'VpcId': vpc_id
        }
        subnet_response = ec2.create_subnet(**subnet_params)
        subnet_id = subnet_response['Subnet']['SubnetId']
        return vpc_id, subnet_id
    except Exception as e:
        print(f"ERROR: VPC creation failed")
        print(f"Error details: {str(e)}")
        return 0

'''
Create security group for ec2
Also creates a sec rule open for all traffic, protocols & ports
return: sec grp id
'''
def create_sec_grp(vpc_id):
    security_group_params = {
        'Description': 'Open Security Group',
        'GroupName': 'OpenSecurityGroup',
        'VpcId': vpc_id
    }
    try:
        response = ec2.create_security_group(**security_group_params)
        security_group_id = response['GroupId']
        try:
            ec2.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {
                        'IpProtocol': '-1',  # All protocols
                        'FromPort': 0,        
                        'ToPort': 65535,     
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}],  
                        'Ipv6Ranges': [{'CidrIpv6': '::/0'}],   
                        'UserIdGroupPairs': [
                            # {'GroupId': security_group_id}
                        ],  
                        'PrefixListIds': []
                    }
                ]
            )
        except Exception as e:
            print(f"ERROR: Security group ingress rule creation failed")
            print(f"Error details: {str(e)}")           
        return security_group_id
    except Exception as e:
        print(f"ERROR: Security group creation failed")
        print(f"Error details: {str(e)}")
        return 0


'''
Generate a key pair
return: file path of priv key
'''
def gen_key_pair(key_name):
    response = ec2.create_key_pair(KeyName=key_name)
    priv_key = response['KeyMaterial']
    priv_key_file_path = f"{key_name}.pem"
    try:
        with open(priv_key_file_path, 'w') as key_file:
            key_file.write(priv_key)
        return priv_key_file_path
    except Exception as e:
        print(f"ERROR: Key pair writing failed")
        print(f"Error details: {str(e)}")
        return 0


'''
Create 3 EC2 instances for etcd nodes
args: num => number of instances
return: an array of instances with elements in the form [instance_id, priv_ip,pub_ip]
''' 
def create_ec2_nodes(sec_grp, subnet_id, key_name, num):
    ami = 'ami-0b0ea68c435eb488d' # Ebs-ssd Linux AMI for us-east-1
    try: 
        response = ec2.run_instances(
            ImageId = ami,
            InstanceType= 't2.micro',
            MinCount = num,
            MaxCount = num,
            KeyName = key_name,
            NetworkInterfaces=[
                {
                    'DeviceIndex': 0,
                    'SubnetId' : subnet_id,
                    'Groups': [
                        sec_grp
                    ],
                    'AssociatePublicIpAddress': True            
                } ]
            )
        instance_ids = [i['InstanceId'] for i in response['Instances']]
        
        print("Waiting for EC2 instances to start...")
        ec2.get_waiter('instance_running').wait(InstanceIds=instance_ids) # Waiting until ec2 instances are ready
        try:
            instance_desc = ec2.describe_instances(InstanceIds=instance_ids)
            # print(f"Instance description: {instance_desc}")
        except Exception as e:
            print(f"Error details: {str(e)}")

        instance_arr = []
        for i in instance_desc['Reservations'][0]['Instances']: # Getting priv & pub ip addrs of instances
            # print(f"##############{i}\n")
            ins_id = i['InstanceId']
            priv_ip = i['PrivateIpAddress']
            pub_ip = i['PublicIpAddress']
            instance_arr.append([ins_id, priv_ip, pub_ip])
        
        return instance_arr

    except Exception as e:
        print(f"ERROR: Ec2 instances creation failed")
        print(f"Error details: {str(e)}")
        return 0


# Etcd setup automation
def main():
    vpc_id, subnet_id = create_vpc()
    sec_grp_id = create_sec_grp(vpc_id)
    print(sec_grp_id)
    priv_key_path = gen_key_pair('saavi')
    instances = create_ec2_nodes(sec_grp_id, subnet_id, 'saavi', 3)
    print(instances)


if __name__ == "__main__":
    main()