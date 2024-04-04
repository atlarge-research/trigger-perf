import etcd3
import os
import argparse
import threading
import time
import logging
import json

# Connecting to etcd cluster
etcd_hosts = ["http://172.31.0.213:2379", "http://172.31.0.15:2379", "http://172.31.0.20:2379"]
etcd = etcd3.Client(host=etcd_hosts)

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

def etcd_put_kv(key: str, value: str):
    etcd.put(key, value)

def etcd_get_kv(key: str):
    etcd.get(key)

def etcd_delete_kv(key: str):
    etcd.delete(key)

def etcd_update_kv(key: str, new_val):
    etcd.put(key, new_val, prev_kv=True)

'''
Function to set watch on given key strings
'''
def set_watch_key(key: str):
    def watch_callback(event):
        recv_time = time.time()
        log_data = {'Key': event.key, 'Event': 'TRIGGER', 'time_stamp': recv_time}
        logger.info(json.dumps(log_data))
        print(f"Key {event.key} has been updated, new value is {event.value}")

    watcher = etcd.watch(key)
    threading.Thread(target=watching_key, args=(watcher, watch_callback)).start()

def watching_key(watcher, callback):
    try:
        while True:
            for event in watcher:
                callback(event)
    except Exception as e:
        print(f" Error occured when watching key: {e}")
        
def string_to_list(string):
    string = string.strip("[]").strip()
    elements = [int(element.strip()) for element in string.split(",")]
    return elements

def main():
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('--ksizes', help='Key sizes to run exp on')
    parser.add_argument('--iters', help='Number of watch measurements')
    parser.add_argument('--val_size', help='Number of watch measurements')
    
    args = parser.parse_args()
    ksizes = string_to_list(args.ksizes)
    iters = int(args.iters)
    val_size = int(args.val_size)



    key_list = [] # list to store keys of given sizes
    for ksize in ksizes:
        temp_key = generate_rand_string(ksize)
        key_list.append(temp_key)

    # Setting watch on key
    for key in key_list:
        set_watch_key(key)

    # put keys and modify them n-1 times
    for key in key_list:
        for i in range(iters):
            val = 'a' # set val size
            send_time = time.time()
            if i == 0:
                etcd_put_kv(key, val)
            else:
                etcd_update_kv(key, val)
            log_data = {'Key': key, 'Event': 'PUT', 'time_stamp': send_time}
            logger.info(json.dumps(log_data))

if __name__ == "__main__":
    main()