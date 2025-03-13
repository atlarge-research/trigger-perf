# TriggerPerf

TriggerPerf is a custom benchmarking tool designed to evaluate the performance of datastore triggers. It currently supports three AWS datastores: S3 Standard, DynamoDB, and AuroraDB. The tool automates trigger setup and configuration, leveraging three Lambda function: Setup, Write, and Receive to create a testbed for benchmarking various trigger mechanisms.

## **Usage**

### **1. Configuration**
All configurations are managed via the `config.yaml` file. This includes:
- **Datastore Parameters**: Define the datastore type and its specific settings.
- **Experiment Details**: Specify key-value sizes, throughput, and other benchmarking parameters.
- **AWS Credentials**: Include the necessary access keys and region information.
- Define experiment details and AWS credentials in `config.yaml`.

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

### **4. Adding a Datastore**
To add support for a new datastore in TriggerPerf:

1. **Create a Driver File**: 
   - Add a new driver file in the `/drivers` directory.
   - Include relevant functions that align with the functionality of existing datastore systems.
   - The driver file should include functions to setup te target system and supporting functions to perform CRUD operations.

2. **Modify Lambda Function**: 
   - Update the file located at `./aws_lambdas/lambdas/initial-lmd.py`.
   - Add the necessary functions to handle the new datastore.

Ensure the new additions follow the structure and conventions of the current implementation to maintain consistency and compatibility.



