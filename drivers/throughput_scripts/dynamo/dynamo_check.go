package main

import (
	"context"
	"crypto/rand"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strconv"
	"sync"
	"time"

	"github.com/akamensky/argparse"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb/types"
)

var logger *log.Logger

func main() {
	fmt.Println("In main func")
	parser := argparse.NewParser("program", "Description of your program")
	// ksizes := parser.String("k", "ksizes", &argparse.Options{Required: true, Help: "give key sizes as a list string"})
	// iters := parser.Int("iters", "", "Number of watch measurements")
	// valSize := parser.Int("v", "val_size", &argparse.Options{Required: true, Help: "Value size"})
	// expType := parser.String("e", "exp_type", &argparse.Options{Required: false, Help: "exp name"})
	err := parser.Parse(os.Args)
	if err != nil {
		fmt.Print(parser.Usage(err))
		return
	}

	// Connect to Dynamo
	// client := dynamoConnect()
	// tableName := "kv_table"

	// Setting up logger
	// logFileName := "dynamo_logging.log"
	// setupLogger(logFileName)

}

func dynamoConnect() *dynamodb.Client {
	// Load the Shared AWS Configuration (~/.aws/config)
	cfg, err := config.LoadDefaultConfig(context.TODO())
	if err != nil {
		log.Fatal("Error getting AwS Credentials", err)
	}
	dynamoClient := dynamodb.NewFromConfig(cfg)

	return dynamoClient
}

func setupLogger(logFileName string) {
	logFile, err := os.OpenFile(logFileName, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatalf("Failed to open log file: %v", err)
	}
	logger = log.New(logFile, "", 0)
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

/*
Generates a string of given size such that last 6 characters as '100000' and rest are random
eg: "ioevnoievb100000"
*/
func genValVersionString(size int) string {
	randBytes := make([]byte, size-6)
	_, err := rand.Read(randBytes)
	if err != nil {
		fmt.Println("Error generating Value version string")
	}

	ver := make([]byte, 6) // generate a '100000' string
	for i := range ver {
		if i == 0 {
			ver[i] = '1'
		} else {
			ver[i] = '0'
		}

	}
	valVersionString := string(randBytes) + string(ver)

	return valVersionString
}

func incrementValVersionString(val string) string {
	verNum := val[len(val)-6:] // As the numeric part if 6 of len

	ver, err := strconv.Atoi(verNum)
	if err != nil {
		fmt.Println("string to int conversion error!")
	}
	ver++ // increment version number

	updatedVerNumStr := strconv.Itoa(ver)
	newValVerStr := val[:len(val)-6] + updatedVerNumStr

	return newValVerStr
}

func getSize(inp_string string) int {
	size := len(inp_string)
	return size
}

func extractVerNum(val string) int {
	verNum := val[len(val)-6:] // As the numeric part if 6 of len

	ver, err := strconv.Atoi(verNum)
	if err != nil {
		fmt.Println("string to int conversion error!")
	}
	return ver
}

func dynamoPutItem(tableName, key, value string, client *dynamodb.Client) error {

	item := map[string]types.AttributeValue{
		"Key": &types.AttributeValueMemberS{
			Value: key,
		},
		"Value": &types.AttributeValueMemberS{
			Value: value,
		},
	}
	input := &dynamodb.PutItemInput{
		TableName: &tableName,
		Item:      item,
	}
	_, err := client.PutItem(context.Background(), input)
	if err != nil {
		log.Printf("failed to put item: %v", err)
		return err
	}
	log.Println("Item added to DynamoDB successfully!")

	return nil
}

/*
Args: KeyList is a list of key strings
*/
func dynamoThroughputExpRunner(keyList []string, valSize int, tableName string, client *dynamodb.Client) {

	val := genValVersionString(valSize)
	expStartTime := time.Now()
	endTime := expStartTime.Add(60 * time.Second)
	rps_ticker := 0 // counter to track requests per second

	for time.Now().Before(endTime) {
		var wg sync.WaitGroup
		for _, key := range keyList {
			wg.Add(1)
			go func(key, val string) {
				sendTime := time.Now().UnixNano()
				dynamoPutItem(tableName, key, val, client)
				rps_ticker++
				keySize := getSize(key)
				ver := extractVerNum(val)
				logData := map[string]interface{}{
					"Key":        key,
					"Event":      "PUT",
					"KeySize":    keySize,
					"KeyVersion": ver,
					"time_stamp": sendTime,
				}
				jsonData, _ := json.Marshal(logData)
				logger.Println(string(jsonData))
				wg.Done()
			}(key, val)
		}
		wg.Wait()
		val = incrementValVersionString(val)
	}
	rps := rps_ticker / 60
	fmt.Println("Requests per second: ")
	fmt.Println(rps)
}
