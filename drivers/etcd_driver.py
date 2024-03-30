import boto3 
from aws import *


ec2 = boto3.client('ec2', region_name='us-east-1')

'''
Creating a VPC with internet access
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
        ec2.modify_vpc_attribute( # CHANGED
            VpcId=vpc_id,
            EnableDnsHostnames={'Value': True}
        )
        # Create Subnet
        subnet_params = {
            'CidrBlock': '172.31.0.0/24',  
            'VpcId': vpc_id
        }
        subnet_response = ec2.create_subnet(**subnet_params)
        subnet_id = subnet_response['Subnet']['SubnetId']
        print(f"VPC created, vpc id: {vpc_id}")
        print(f"Subnet id: {subnet_id}")

        # Create Internet Gateway
        internet_gateway_response = ec2.create_internet_gateway()
        internet_gateway_id = internet_gateway_response['InternetGateway']['InternetGatewayId']
        print(f"Internet Gateway created, id: {internet_gateway_id}")

        # Attach Internet Gateway to VPC
        ec2.attach_internet_gateway(
            InternetGatewayId=internet_gateway_id,
            VpcId=vpc_id
        )
        route_table_response = ec2.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
        route_table_id = route_table_response['RouteTables'][0]['RouteTableId']
        ec2.create_route(
            RouteTableId=route_table_id,
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=internet_gateway_id
        )

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
                        'FromPort': -1,        
                        'ToPort': -1,     
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}],  
                        'Ipv6Ranges': [{'CidrIpv6': '::/0'}],   
                        'UserIdGroupPairs': [],  
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
return: an array of instances with elements in the form [[instance_id, priv_ip,pub_ip], ...]
''' 
def create_ec2_nodes(sec_grp, subnet_id, key_name, num, acc_id):
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
            # IamInstanceProfile={
            #     'Arn': f'arn:aws:iam::{acc_id}:instance-profile/myEC2Role'
            #     # 'Name': 'myEC2Role'
            # }
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
            ins_id = i['InstanceId']
            priv_ip = i['PrivateIpAddress']
            pub_ip = i['PublicIpAddress']
            instance_arr.append([ins_id, priv_ip, pub_ip])
        print(f"{num} EC2 instances ready!")
        return instance_arr

    except Exception as e:
        print(f"ERROR: Ec2 instances creation failed")
        print(f"Error details: {str(e)}")
        return 0
    

'''
Genrates config files for the 3 etcd nodes
args: list of instance ips(output from create_ec2_nodes)
return: list of config for each node as str
'''
def gen_etcd_configs(inst_list):
    node1_ip = inst_list[0][1]   # getting node priv ips
    node2_ip = inst_list[1][1]
    node3_ip = inst_list[2][1]
    node_ip = 4
    node_configs_list = []
    for i in range(len(inst_list)):
        node_ip = inst_list[i][1]
        config_template = f"ETCD_NAME=etcd{i+1}\nETCD_DATA_DIR=/var/lib/etcd\nETCD_LISTEN_CLIENT_URLS=http://{node_ip}:2379,http://127.0.0.1:2379\nETCD_LISTEN_PEER_URLS=http://{node_ip}:2380\nETCD_ADVERTISE_CLIENT_URLS=http://{node_ip}:2379\nETCD_INITIAL_ADVERTISE_PEER_URLS=http://{node_ip}:2380\nETCD_INITIAL_CLUSTER=etcd1=http://{node1_ip}:2380,etcd2=http://{node2_ip}:2380,etcd3=http://{node3_ip}:2380\nETCD_INITIAL_CLUSTER_STATE=new\nETCD_INITIAL_CLUSTER_TOKEN=etcd-cluster\n"
        node_configs_list.append(config_template)
    print(f"Etcd Configs generated!")
    return node_configs_list


'''
Sets up Etcd on given EC2 instance
args: ec2 instance id, config of that node
'''
def setup_etcd_on_ec2(inst_id, config):
    ssm = boto3.client('ssm', region_name='us-east-1')

    commands = [
    "sudo apt update",
    "sudo su",
    'wget -q --show-progress "https://github.com/etcd-io/etcd/releases/download/v3.5.0/etcd-v3.5.0-linux-amd64.tar.gz"',
    "tar zxf etcd-v3.5.0-linux-amd64.tar.gz",
    "mv etcd-v3.5.0-linux-amd64/etcd* /usr/bin/",
    "chmod +x /usr/bin/etcd*",
    f"echo '{config}' | sudo tee /etc/etcd",
    "echo '[Unit]\nDescription=etcd\n\n[Service]\nType=notify\nEnvironmentFile=/etc/etcd\nExecStart=/usr/bin/etcd\nRestart=on-failure\nRestartSec=5\n\n[Install]\nWantedBy=multi-user.target\n' | sudo tee /etc/systemd/system/etcd.service",
    "systemctl daemon-reload",
    "systemctl enable etcd",
    "service etcd start"
    ]
    try:
        for command in commands:
            response = ssm.send_command(
                InstanceIds=[inst_id],
                DocumentName="AWS-RunShellScript",
                Parameters={'commands': [command]}
            )
            # print(response)
        return 0
    except Exception as e:
        print(f"ERROR: Etcd setup failed (tried using ssm)")
        print(f"Error details: {str(e)}")
        return 0


'''
Prints out etcd cluster members details
args: node_ip(first node priv ip)
'''
def etcd_verify_cluster(inst_dets):
    ssm = boto3.client('ssm', region_name='us-east-1')
    inst_id = inst_dets[0]
    node_ip = inst_dets[1]
    cluster_status_cmd = f'etcdctl --endpoints=http://{node_ip}:2379 member list'
    try:
        response = ssm.send_command(
            InstanceIds=[inst_id],
            DocumentName="AWS-RunShellScript",
            Parameters={'commands': [cluster_status_cmd]}
        )
        # print(response)
        return 0
    except Exception as e:
        print(f"ERROR: Etcd setup verification failed (tried using ssm)")
        print(f"Error details: {str(e)}")
        return 0


'''
Etcd Master Setup Func
'''
def etcd_setup_master(acc_id):
    # Vpc and other setup
    vpc_id, subnet_id = create_vpc()
    sec_grp_id = create_sec_grp(vpc_id)
    print(sec_grp_id)
    priv_key_path = gen_key_pair('saavi')
    role_arn, inst_prof_arn = create_aws_ec2_role('myEC2Role', 'us-east-1')

    # Creating ec2 instances
    etcd_insts = create_ec2_nodes(sec_grp_id, subnet_id, 'saavi', 3, acc_id)
    print(etcd_insts)

    # Etcd node config generation
    node_configs = gen_etcd_configs(etcd_insts)
    print("#### CONFIGS START\n")
    print(node_configs)

    # Attaching role to instances
    for i in range(len(etcd_insts)):
        inst_id = etcd_insts[i][0]
        attach_role_to_ec2(inst_id, 'myEC2Role', inst_prof_arn)
        # setup_etcd_on_ec2(inst_id, node_configs[i])

    time.sleep(300) # sleeping for ssm to be setup
    # Setting up etcd on all nodes
    for i in range(len(etcd_insts)):
        inst_id = etcd_insts[i][0]
        setup_etcd_on_ec2(inst_id, node_configs[i])

    print("Etcd setup complete on all nodes")

    return 0


# Etcd write kv pair

# Etcd setup watch


def main():
    vpc_id, subnet_id = create_vpc()
    sec_grp_id = create_sec_grp(vpc_id)
    print(sec_grp_id)
    priv_key_path = gen_key_pair('saavi')
    instances = create_ec2_nodes(sec_grp_id, subnet_id, 'saavi', 3)
    print(instances)


if __name__ == "__main__":
    acc_id = 133132736141
    # etcd_setup_master(acc_id)
    etcd_insts = [['i-08db15828db8804f2', '172.31.0.116', '3.93.182.47'], ['i-00d2f7e2f251f33d4', '172.31.0.232', '54.224.92.225'], ['i-0535f24b75038d791', '172.31.0.253', '54.83.93.180']]
    node_configs = ['ETCD_NAME=etcd0\nETCD_DATA_DIR=/var/lib/etcd\nETCD_LISTEN_CLIENT_URLS=http://172.31.0.116:2379,http://127.0.0.1:2379\nETCD_LISTEN_PEER_URLS=http://172.31.0.116:2380\nETCD_ADVERTISE_CLIENT_URLS=http://172.31.0.116:2379\nETCD_INITIAL_ADVERTISE_PEER_URLS=http://172.31.0.116:2380\nETCD_INITIAL_CLUSTER=etcd1=http://172.31.0.116:2380,etcd2=http://172.31.0.232:2380,etcd3=http://172.31.0.253:2380\nETCD_INITIAL_CLUSTER_STATE=new\nETCD_INITIAL_CLUSTER_TOKEN=etcd-cluster\n', 'ETCD_NAME=etcd1\nETCD_DATA_DIR=/var/lib/etcd\nETCD_LISTEN_CLIENT_URLS=http://172.31.0.232:2379,http://127.0.0.1:2379\nETCD_LISTEN_PEER_URLS=http://172.31.0.232:2380\nETCD_ADVERTISE_CLIENT_URLS=http://172.31.0.232:2379\nETCD_INITIAL_ADVERTISE_PEER_URLS=http://172.31.0.232:2380\nETCD_INITIAL_CLUSTER=etcd1=http://172.31.0.116:2380,etcd2=http://172.31.0.232:2380,etcd3=http://172.31.0.253:2380\nETCD_INITIAL_CLUSTER_STATE=new\nETCD_INITIAL_CLUSTER_TOKEN=etcd-cluster\n', 'ETCD_NAME=etcd2\nETCD_DATA_DIR=/var/lib/etcd\nETCD_LISTEN_CLIENT_URLS=http://172.31.0.253:2379,http://127.0.0.1:2379\nETCD_LISTEN_PEER_URLS=http://172.31.0.253:2380\nETCD_ADVERTISE_CLIENT_URLS=http://172.31.0.253:2379\nETCD_INITIAL_ADVERTISE_PEER_URLS=http://172.31.0.253:2380\nETCD_INITIAL_CLUSTER=etcd1=http://172.31.0.116:2380,etcd2=http://172.31.0.232:2380,etcd3=http://172.31.0.253:2380\nETCD_INITIAL_CLUSTER_STATE=new\nETCD_INITIAL_CLUSTER_TOKEN=etcd-cluster\n']
    for i in range(len(etcd_insts)):
        inst_id = etcd_insts[i][0]
        setup_etcd_on_ec2(inst_id, node_configs[i])



# ansible-playbook site.yml -i inventory/my-cluster/hosts.ini --private-key ../inventory/vm-private.pem