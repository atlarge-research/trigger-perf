# TriggerPerf

TriggerPerf is a custom benchmarking tool designed to evaluate the performance of datastore triggers. It currently supports three AWS datastores: S3 Standard, DynamoDB, and AuroraDB. The tool automates trigger setup and configuration, leveraging three Lambda function: Setup, Write, and Receive to create a testbed for benchmarking various trigger mechanisms. Currently TriggerPerf supports S3 Event Notifications, DynamoDB Streams and AuroraDB UDF triggers.

## **Usage**

### **1. Configuration**
All configurations are managed via the `config.yaml` file. This includes:
- **Datastore Parameters**: Define the datastore type and its specific settings.
- **Experiment Details**: Specify key-value sizes, throughput, and other benchmarking parameters.
- **AWS Credentials**: Include the necessary access keys and region information.
- Define experiment details and AWS credentials in `config.yaml`.
```bash
## other inputs: "s3", "etcd", "dynamo", "aurora"
data_store: "dynamo"
aws_acc_id: xxxxxxxxxx
region: us-east-1 
```

### **2. Setup & Run**
Run the `setup.py` script to initialize and configure the benchmarking environment:
- Deploys the **Setup**, **Write**, and **Receive** Lambda functions.
- Configures the triggers for the selected datastore.
- Integrates AWS CloudWatch for logging and performance metrics collection.
After setup, run the `main.py` script to start the experiments defined in `config.yaml`

```bash
python setup.py
python main.py
```

### **3. Logs & Teardown**
- **Logs**: Filtered logs are automatically saved to the `/logs` directory for later analysis. Run the `/proc_logs/latency_data_processing.ipynb` to generate graphs.
```bash
python teardown.py 
```
- **Teardown**: To remove all datastore and trigger configurations from your AWS account, run the `teardown.py` script:

```bash
python teardown.py 
```

### **4. Extending TriggerPerf: Adding a New Datastore**

To add support for a new datastore, follow these steps:

### **Step 1: Create a Driver File**
- Add a new driver file inside the `/drivers` directory.
- Implement necessary functions that align with the functionality of existing datastore integrations.
- The driver should include functions for:
  - **Setting up the target datastore.**
  - **Performing CRUD operations.**

### **Step 2: Modify Lambda Functions**
- **Update `./aws_lambdas/lambdas/initial-lmd.py`**:  
  Add functions required to connect and interact with the new datastore.
- **Update `./aws_lambdas/lambdas/recv-lmd.py`**:  
  Implement functions to handle the datastore's trigger mechanism.

### **Step 3: Maintain Consistency & Compatibility**
- Ensure the new integration adheres to TriggerPerf’s existing structure and conventions.
- This maintains seamless compatibility with the benchmarking framework.




