import etcd3
import os
import time

# Connect to etcd cluster
etcd_hosts = ["http://etcd1-ip:2379", "http://etcd2-ip:2379", "http://etcd3-ip:2379"]
etcd = etcd3.Client(host=etcd_hosts)

def generate_rand_string(size: int):
    # size is in bytes
    random_bytes = os.urandom(size)
    random_string = random_bytes.decode('latin-1')  # Decode bytes to string
    return random_string

def etcd_put_kv(key: str, value: str):
    etcd.put(key, value)

def etcd_get_kv(key: str):
    etcd.get(key)

def watch_key(key: str):
    watcher = etcd.watch(key)
    for event in watcher:
        print(f"Key {event.key} has been updated, new value is {event.value}")

'''
Function to set watch on given key strings
'''
def set_watch_on_key(key: str):
    pass


# get key sizes input as list 
# iter number 


if __name__ == "__main__":
    key_list = []