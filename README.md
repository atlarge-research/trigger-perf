# TriggerPerf

TriggerPerf is a custom benchmarking tool designed to evaluate the performance of datastore triggers. It currently supports three AWS datastores: S3 Standard, DynamoDB, and AuroraDB. The tool automates trigger setup and configuration, leveraging three Lambda functions—Setup, Write, and Receiv to create a testbed for benchmarking various trigger mechanisms.

## **Usage**

### **1. Configuration**
All configurations are managed via the `config.yaml` file. This includes:
- **Datastore Parameters**: Define the datastore type and its specific settings.
- **Experiment Details**: Specify key-value sizes, throughput, and other benchmarking parameters.
- **AWS Credentials**: Include the necessary access keys and region information.

### **2. Setup**
Run the `setup.py` script to initialize and configure the benchmarking environment:
- Deploys the **Setup**, **Write**, and **Receive** Lambda functions.
- Configures the triggers for the selected datastore.
- Integrates AWS CloudWatch for logging and performance metrics collection.

```bash
python setup.py
```
