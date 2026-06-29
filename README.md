# AWS Serverless Weather ETL Pipeline

## Project Overview

This project implements a **serverless ETL (Extract, Transform, Load) pipeline** using AWS services. The pipeline automatically processes weather data whenever a CSV file is uploaded to an Amazon S3 bucket.

The solution uses **Amazon S3** as the data source, **AWS Lambda** for ETL processing, **Amazon DynamoDB** for storing cleaned records, and **Amazon CloudWatch** for monitoring and logging.

---

# Architecture

```
                Upload CSV
                    │
                    ▼
          Amazon S3 Bucket (raw/)
                    │
        ObjectCreated Event Trigger
                    │
                    ▼
            AWS Lambda Function
                    │
        ┌───────────┼────────────┐
        │           │            │
        ▼           ▼            ▼
    Extract     Transform      Validate
                    │
                    ▼
            Clean Weather Data
                    │
                    ▼
         Amazon DynamoDB Table
                    │
                    ▼
         Amazon CloudWatch Logs
```

---

# Technology Stack

| Service | Purpose |
|----------|---------|
| AWS Lambda | Serverless ETL processing |
| Amazon S3 | Store raw CSV files |
| Amazon DynamoDB | Store cleaned weather records |
| Amazon CloudWatch | Logging and monitoring |
| AWS IAM | Access control and permissions |
| Python 3.11 | Lambda runtime |

---

# Project Workflow

```
Upload CSV
     │
     ▼
Amazon S3 (raw/)
     │
ObjectCreated Event
     │
     ▼
AWS Lambda
     │
     ├── Read CSV
     ├── Validate Records
     ├── Clean Data
     ├── Transform Data
     ├── Load into DynamoDB
     └── Generate Audit Logs
                │
                ▼
        Amazon CloudWatch
```

---

# Project Structure

```
weather-etl/
│
├── lambda_function.py
├── sample_weather.csv
├── README.md
└── requirements.txt
```

---

# Step 1 – Create Amazon S3 Bucket

Created an S3 bucket to store incoming weather datasets.

### Bucket Name

```
weather-etl-manu
```

### Folder Structure

```
weather-etl-manu
│
├── raw/
│
└── processed/
```

### Purpose

- Store raw weather CSV files
- Automatically trigger Lambda whenever a new CSV is uploaded

---

# Step 2 – Create DynamoDB Table

Created a DynamoDB table to store cleaned weather records.

### Table Name

```
clean_records
```

### Partition Key

```
record_id (String)
```

### Stored Attributes

- record_id
- city
- temperature
- humidity
- status
- processed_at

---

# Step 3 – Create Lambda Function

Created a Lambda function to perform the ETL process.

### Configuration

| Setting | Value |
|----------|-------|
| Function Name | weather-etl |
| Runtime | Python 3.11 |
| Architecture | x86_64 |

### Responsibilities

- Read CSV from Amazon S3
- Validate weather records
- Remove invalid data
- Clean and standardize records
- Generate derived fields
- Insert data into DynamoDB
- Write audit logs to CloudWatch

---

# Step 4 – Configure S3 Trigger

Configured Amazon S3 to invoke Lambda automatically.

| Setting | Value |
|----------|-------|
| Bucket | weather-etl-manu |
| Event | ObjectCreated |
| Prefix | raw/ |
| Suffix | .csv |

Whenever a CSV file is uploaded into:

```
weather-etl-manu/raw/
```

Lambda is triggered automatically.

---

# Step 5 – Configure IAM Permissions

The Lambda execution role was granted permissions to access AWS resources.

### Attached Policies

- AWSLambdaBasicExecutionRole
- AmazonS3FullAccess
- AmazonDynamoDBFullAccess_v2

These permissions allow Lambda to:

- Read files from Amazon S3
- Write records into DynamoDB
- Generate CloudWatch logs

---

# Step 6 – Develop ETL Logic

The Lambda function performs the following ETL stages.

## Extract

Reads the uploaded CSV file from Amazon S3.

```
Amazon S3
      │
      ▼
Read CSV
```

---

## Transform

Each record is validated and cleaned.

### Validation Rules

Required Fields

- record_id
- city
- temperature
- humidity

Temperature Range

```
-90°C to 60°C
```

Humidity Range

```
0% to 100%
```

### Data Cleaning

- Remove leading/trailing spaces
- Standardize city names using Title Case
- Convert numeric values
- Reject invalid records

### Derived Field

Weather status is generated based on temperature.

| Temperature | Status |
|-------------|--------|
| Below 15°C | Cold |
| 15°C – 29.99°C | Normal |
| 30°C and Above | Hot |

---

## Load

Valid records are batch inserted into the DynamoDB table.

```
Clean Records
      │
      ▼
DynamoDB (clean_records)
```

---

## Audit Logging

Each execution generates an audit summary in Amazon CloudWatch.

Example

```json
{
  "files_processed": 1,
  "total_input_records": 40,
  "inserted_records": 34,
  "rejected_records": 6
}
```

---

# Step 7 – Upload Weather Dataset

Uploaded the sample dataset.

```
sample_weather_v3.csv
```

Location

```
weather-etl-manu/raw/
```

Uploading the file generated an **ObjectCreated** event that automatically invoked the Lambda function.

---

# Step 8 – Lambda Execution

The Lambda function performed the following operations.

- Read CSV from Amazon S3
- Validated all records
- Removed invalid rows
- Generated weather status
- Inserted valid records into DynamoDB
- Logged execution summary

Execution Summary

| Metric | Value |
|---------|------:|
| Files Processed | 1 |
| Total Records | 40 |
| Inserted Records | 34 |
| Rejected Records | 6 |

---

# Step 9 – Verify DynamoDB

Verified that transformed records were successfully stored in the **clean_records** table.

Example Records

| record_id | city | temperature | humidity | status |
|-----------|------|------------:|---------:|--------|
| 1010 | Mumbai | 32.8 | 88 | Hot |
| 1028 | Toronto | 12.1 | 57 | Cold |
| 1037 | Chennai | 31.0 | 82 | Hot |

---

# Step 10 – Monitor Using CloudWatch

Amazon CloudWatch was used to monitor Lambda execution.

CloudWatch logs include:

- File being processed
- Processing status
- Number of inserted records
- Number of rejected records
- Execution duration
- Audit summary

Example

```
Processing file:
s3://weather-etl-manu/raw/sample_weather_v3.csv

Files Processed : 1
Total Records   : 40
Inserted Records: 34
Rejected Records: 6
```

---

# End-to-End Workflow

```
Start
  │
  ▼
Upload CSV File
  │
  ▼
Amazon S3 Bucket (raw/)
  │
  ▼
ObjectCreated Event
  │
  ▼
AWS Lambda Triggered
  │
  ▼
Extract CSV Data
  │
  ▼
Validate Records
  │
  ▼
Clean & Transform Data
  │
  ▼
Generate Weather Status
  │
  ▼
Load Clean Records into DynamoDB
  │
  ▼
Generate Audit Logs
  │
  ▼
Amazon CloudWatch
  │
  ▼
End
```

---

# Key Features

- Fully serverless architecture
- Automatic event-driven processing
- Real-time CSV ingestion
- Data validation and cleaning
- Weather status derivation
- Batch insertion into DynamoDB
- CloudWatch logging and auditing
- Secure access using IAM roles

---

# Project Outcome

Successfully developed an end-to-end serverless ETL pipeline using AWS services.

The pipeline automatically:

- Detects newly uploaded weather CSV files in Amazon S3.
- Triggers AWS Lambda using S3 events.
- Validates and transforms weather data.
- Rejects invalid records.
- Stores cleaned records in Amazon DynamoDB.
- Logs execution details and audit summaries in Amazon CloudWatch.

This implementation demonstrates an event-driven, scalable, and fully managed serverless data processing workflow on AWS.
