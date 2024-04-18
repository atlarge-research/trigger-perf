import etcd3
import os
import argparse
import threading
import time
import logging
import json
import traceback
import psutil
import etcd3.exceptions

# Connecting to etcd cluster
etcd1_ip = '172.31.0.15'
etcd2_ip = '172.31.0.20'
etcd3_ip = '172.31.0.213'
etcd_hosts = ["http://{}:2379".format(etcd1_ip), "http://{}:2379".format(etcd2_ip), "http://{}:2379".format(etcd3_ip)]


try:
    etcd = etcd3.client(host='172.31.0.217', port=2379)
    print(f"Connection success!, etcd version: {etcd.status().version}")
except etcd3.exceptions.ConnectionFailedError as e:
    print(e)
    traceback.print_exc()
    print("connection failed!")


# Logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_file = 'etcd_logging.log'
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

def generate_rand_string(size: int):
    # size is in bytes
    random_bytes = os.urandom(size)
    random_string = random_bytes.decode('latin-1')  # Decode bytes to string
    return random_string

def get_size(input_string):
    # Calculate the size of the input string in bytes
    string_bytes = input_string.encode('latin-1')  # Encode string to bytes
    size_in_bytes = len(string_bytes)
    return size_in_bytes

'''
Etcd CRUD operations
'''
def etcd_put_kv(key: str, value: str):
    etcd.put(key, value)
    # print(f"\nKV pair inserted => {key}:{value}")

def etcd_get_kv(key: str):
    etcd.get(key)

def etcd_delete_kv(key: str):
    etcd.delete(key)
    print(f"Key deleted => {key}")

def etcd_update_kv(key: str, new_val):
    etcd.put(key, new_val, prev_kv=True)

'''
Function to set watch on given key 
'''
def watch_callback(event, key, watch_flag):
    # print(event.events)
    for e in event.events:
        recv_time = time.time()
        e_version = e.version
        check_key = e.key.decode("utf-8")
        
        key_size = get_size(key)
        log_data = {'Key': key, 'Event': 'TRIGGER', 'KeySize': key_size, 'KeyVersion': e_version, 'time_stamp': recv_time}
        print(log_data)
        logger.info(json.dumps(log_data))
        # print(f"Key {key} has been updated, new value is")
        if watch_flag == -1: # Throughput run
            return
        else:   # Latency run
            watch_flag.set()
            return 

'''
Sets watch on a given key
for latency exp: exits after one watch event
for throughput exp: keeps looping until keyboard intr
Args: Watch flag is -1 in throughput experiment
'''
def set_watch_key(key: str, watch_flag):
    if watch_flag == -1: # Throughput experiment
        watch_id = etcd.add_watch_callback(key, lambda event: watch_callback(event, key, watch_flag))
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print(f"Stopped watching key: {key}")
            etcd.cancel_watch(watch_id)
    else:
        watch_id = etcd.add_watch_callback(key, lambda event: watch_callback(event, key, watch_flag))
        try:
            watch_flag.wait()
        except KeyboardInterrupt:
            print(f"Stopped watching key: {key}")
        finally:
            etcd.cancel_watch(watch_id)
            return
    
def string_to_list(string):
    string = string.strip("[]").strip()
    elements = [int(element.strip()) for element in string.split(",")]
    return elements

'''
To create iter number of keys for each ksize and compute watch latency
'''
def watch_latency_exp_runner(ksizes, iters, val_size):
    # generate iter number of keys for each key size
    key_list = []
    for i in range(iters):
        for ks in ksizes:
            temp_key = generate_rand_string(ks)
            key_list.append(temp_key)
    print(f"Key list len: {len(key_list)}")
    
    time.sleep(3) # sleeping for watch setup to complete
    val = generate_rand_string(val_size)
    threads = []
    for key in key_list:
        watch_flag = threading.Event()
        watch_thread = threading.Thread(target=set_watch_key, args=(key, watch_flag))
        watch_thread.start()
        time.sleep(1)
        send_time = time.time()
        etcd_put_kv(key, val)
        key_size = get_size(key)
        log_data = {'Key': key, 'Event': 'PUT', 'KeySize': key_size, 'KeyVersion': 1, 'time_stamp': send_time}
        print(log_data)
        logger.info(json.dumps(log_data))
        watch_thread.join()
    return
        

'''
Creates one key for each ksize and keeps modifing it for a minute.
Keys are modified in a round robin fashion continously.
Values need to be recorded only when the CPU utilization% is above 75%
'''            
def watch_throughput_exp_runner(ksizes, val_size):
    print("Throughput Experiment Started!")
    key_list = [] # list to store keys of given sizes
    for ksize in ksizes:
        temp_key = generate_rand_string(ksize)
        key_list.append(temp_key)
    print(key_list)

    # Setting watch on key
    watch_threads = []
    for key in key_list:
        watch_flag = -1
        try:
            thread = threading.Thread(target=set_watch_key, args=(key,watch_flag))
            thread.start()
            watch_threads.append(thread)
        except Exception as e:
            print(f"Setting watch on key {key} failed with error {e}")

    # put keys and modify them n-1 times in round robin
    val = generate_rand_string(val_size)
    exp_start_time = time.time()
    end_time = exp_start_time + 60 
    ver = 0 # key version number
    while time.time() < end_time:
        for key in key_list:
            send_time = time.time()
            if ver % 5 == 0:
                    cpu_utilization = psutil.cpu_percent()
                    cu = cpu_utilization # flag to indicate if cpu utilization is above 75%
                # etcd_put_kv(key, val)
            # else:
            #     etcd_update_kv(key, val)
            etcd_put_kv(key, val)
            key_size = get_size(key)
            log_data = {'Key': key, 'Event': 'PUT', 'KeySize': key_size, 'KeyVersion': ver+1, 'time_stamp': send_time, 'CPU': cu}
            print(log_data)
            logger.info(json.dumps(log_data))
        ver += 1
    print("Throughput Experiment Complete!")


def main():
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('--ksizes', help='Key sizes to run exp on')
    parser.add_argument('--iters', help='Number of watch measurements')
    parser.add_argument('--val_size', help='Number of watch measurements')
    parser.add_argument('--exp_type', help='Latency or Throughput experiment') # latency or throughput

    args = parser.parse_args()
    ksizes = string_to_list(args.ksizes)
    iters = int(args.iters)
    val_size = int(args.val_size)
    exp_type = args.exp_type

    if exp_type == 'latency':
        watch_latency_exp_runner(ksizes, iters, val_size)
    elif exp_type == 'throughput':
        watch_throughput_exp_runner(ksizes, val_size)

'''
Note: delete etcd_logging.log before running
Sample run command:
python3.7 etcd_watch_script.py --ksizes [5,10] --iters 3 --val_size 10 --exp_type latency
python3.7 etcd_watch_script.py --ksizes [5,10] --iters 3 --val_size 10 --exp_type throughput
'''
if __name__ == "__main__":
    main()
    # set_watch_key("key1")
    # etcd_put_kv("key1", "bsdk")
    # python3.7 etcd_watch_script.py --ksizes [27,59,93] --iters 50 --val_size 889 --exp_type latency