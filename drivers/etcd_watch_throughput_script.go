package main

import (
	"context"
	"crypto/rand"
	"fmt"
	"log"
	"time"

	clientv3 "go.etcd.io/etcd/client/v3"
)

// var (
// 	etcdClient *clientv3.Client
// )

func main() {
	fmt.Println("In main func")
	// Define the endpoints of the etcd cluster
	endpoints := []string{"http://54.152.142.33:2379"}

	// Create a new etcd client
	client, err := clientv3.New(clientv3.Config{
		Endpoints:   endpoints,
		DialTimeout: 5 * time.Second,
	})
	if err != nil {
		log.Fatal("Error connecting to etcd:", err)
	}
	defer client.Close()

	// Verify the connection by getting the cluster status
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	resp, err := client.Status(ctx, endpoints[0])
	if err != nil {
		log.Fatal("Error getting etcd cluster status:", err)
	}
	fmt.Println("Cluster ID:", resp.Header.ClusterId)
	fmt.Println("Successfully connected to etcd cluster!")

}

func etcdPutKV(client *clientv3.Client, key, value string) error {
	_, err := client.Put(context.Background(), key, value)
	return err
}

func getRandStrings(size int) (string, error) {
	rand_bytes := make([]byte, size)
	_, err := rand.Read(rand_bytes)
	if err != nil {
		return "", err
	}
	rand_string := string(rand_bytes)
	return rand_string, err
}

func getSize(inp_string string) int {
	size := len(inp_string)
	return size
}

func watchThroughputExpRunner(ksizes []int, valSize int) {

	keyList := make([]string, 0) // list to store keys of given sizes
	for _, ks := range ksizes {
		tempKey, _ := getRandStrings(ks)
		keyList = append(keyList, tempKey)
	}
	return
}

func setWatchKey(key string) {

}

func watchCallback(event, key string) {

}
