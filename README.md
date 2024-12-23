# TriggerPerf

TriggerPerf is a custom benchmarking tool designed to evaluate the performance of datastore triggers. It currently supports three AWS datastores: S3 Standard, DynamoDB, and AuroraDB. The tool automates trigger setup and configuration, leveraging three Lambda functions—Setup, Write, and Receiv to create a testbed for benchmarking various trigger mechanisms.

## **Usage**

### **1. Configuration**
All configurations are managed via the `config.yaml` file. This includes:
- **Datastore Parameters**: Define the datastore type and its specific settings.
- **Experiment Details**: Specify key-value sizes, throughput, and other benchmarking parameters.
- **AWS Credentials**: Include the necessary access keys and region information.

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
- **Logs**: Filtered logs are automatically saved to the `/logs` directory for later analysis.
- **Teardown**: To remove all datastore and trigger configurations from your AWS account, run the `teardown.py` script:

```bash
python teardown.py 
```

### **4. Adding a Datastore**
To add a datastore, users need to add a driver file to the `/drivers` folders with relevant functions similar to current systems. A few functions also need to be added to the file at `./aws_lambdas/lambdas/initial-lmd.py`




