import etcd3
import time

# Connect to etcd cluster
etcd_hosts = ["http://etcd1-ip:2379", "http://etcd2-ip:2379", "http://etcd3-ip:2379"]
etcd = etcd3.Client(host=etcd_hosts)


def etcd_put_kv(key, value):
    etcd.put(key, value)

def etcd_get_kv(key):
    etcd.get(key)
