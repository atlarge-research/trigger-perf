# TriggerPerf

A custom tool for benchmarking datastore trigger performance. Currently it works for 3 datastores in the AWS ecosystem: S3 Standard, DynamoDB, AuroraDB. The tool does automatic trigger setup and configuration.
For this it uses 3 lambda functions: Setup, Write and Receive. 

## Usage
