package main

import (
	"context"
	"crypto/rand"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/akamensky/argparse"
	clientv3 "go.etcd.io/etcd/client/v3"
)

var logger *log.Logger

/*
Sample run cmd:
go run etcd_watch_throughput.go --ksizes [5,8] --val_size 20
*/
func main() {
	fmt.Println("In main func")
	parser := argparse.NewParser("program", "Description of your program")
	ksizes := parser.String("k", "ksizes", &argparse.Options{Required: true, Help: "give key sizes as a list string"})
	// iters := parser.Int("iters", "", "Number of watch measurements")
	valSize := parser.Int("v", "val_size", &argparse.Options{Required: true, Help: "Value size"})
	// expType := parser.String("e", "exp_type", &argparse.Options{Required: false, Help: "exp name"})
	err := parser.Parse(os.Args)
	if err != nil {
		fmt.Print(parser.Usage(err))
		return
	}

	// Connect to Etcd cluster
	etcd := etcdConnect()

	// Setting up logger
	logFileName := "etcd_logging.log"
	setupLogger(logFileName)

	// Convert ksizes string to list
	ksizes_l := strToList(*ksizes)

	// Main runner
	watchThroughputExpRunner(ksizes_l, *valSize, etcd)

}

func etcdConnect() *clientv3.Client {

	endpoints := []string{"http://172.31.0.217:2379"}
	client, err := clientv3.New(clientv3.Config{
		Endpoints:   endpoints,
		DialTimeout: 5 * time.Second,
	})
	if err != nil {
		log.Fatal("Error connecting to etcd:", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	resp, err := client.Status(ctx, endpoints[0])
	if err != nil {
		log.Fatal("Error getting etcd cluster status:", err)
	}
	fmt.Println("Cluster ID:", resp.Header.ClusterId)
	fmt.Println("Successfully connected to etcd cluster!")
	return client
}

func setupLogger(logFileName string) {
	logFile, err := os.OpenFile(logFileName, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatalf("Failed to open log file: %v", err)
	}
	logger = log.New(logFile, "", 0)
}

func etcdPutKV(key, value string, etcd *clientv3.Client) error {
	_, err := etcd.Put(context.Background(), key, value)
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

func strToList(list_str string) []int {
	trimmed := strings.Trim(list_str, "[]")
	elements := strings.Split(trimmed, ",")
	result := make([]int, len(elements))

	for i, element := range elements {
		num, _ := strconv.Atoi(strings.TrimSpace(element))
		result[i] = num
	}
	return result
}
func watchThroughputExpRunner(ksizes []int, valSize int, etcd *clientv3.Client) {

	keyList := make([]string, 0) // list to store keys of given sizes
	for _, ks := range ksizes {
		tempKey, _ := getRandStrings(ks)
		keyList = append(keyList, tempKey)
	}

	for _, key := range keyList {
		setWatchKey(key, etcd)
	}
	val, _ := getRandStrings(valSize)
	expStartTime := time.Now()
	endTime := expStartTime.Add(60 * time.Second)
	ver := 0
	rps_ticker := 0 // counter to track requests per second

	for time.Now().Before(endTime) {
		var wg sync.WaitGroup
		for _, key := range keyList {
			wg.Add(1)
			go func(key string) {
				sendTime := time.Now().UnixNano()
				etcdPutKV(key, val, etcd)
				rps_ticker++
				keySize := getSize(key)
				logData := map[string]interface{}{
					"Key":        key,
					"Event":      "PUT",
					"KeySize":    keySize,
					"KeyVersion": ver + 1,
					"time_stamp": sendTime,
				}
				jsonData, _ := json.Marshal(logData)
				// fmt.Println(string(jsonData))
				logger.Println(string(jsonData))
				wg.Done()
			}(key)
		}
		wg.Wait()
		ver++
	}
	rps := rps_ticker / 60
	fmt.Println("Requests per second: ")
	fmt.Println(rps)
}

func setWatchKey(key string, etcd *clientv3.Client) {
	// msg := fmt.Sprintf("Setting watch for key %s", key)
	// fmt.Println((msg))
	ctx := context.Background()
	watchChan := etcd.Watch(ctx, key)
	go func() {
		for watchResp := range watchChan {
			// fmt.Println(watchResp)
			watchCallback(watchResp, key)
		}
	}()
}

func watchCallback(watchResp clientv3.WatchResponse, key string) {

	for _, event := range watchResp.Events {
		recvTime := time.Now().UnixNano()
		eVersion := event.Kv.Version
		// checkKey := string(event.Kv.Key)
		keySize := len(key)
		logData := map[string]interface{}{
			"Key":        key,
			"Event":      "TRIGGER",
			"KeySize":    keySize,
			"KeyVersion": eVersion,
			"time_stamp": recvTime,
		}
		jsonData, _ := json.Marshal(logData)
		// fmt.Println(string(jsonData))
		logger.Println(string(jsonData))
	}
}
