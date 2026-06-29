# AWS Serverless Weather ETL Pipeline with CI/CD

## Project Overview

This project implements a **serverless ETL (Extract, Transform, Load) pipeline** on AWS for processing weather data. Whenever a CSV file is uploaded to an Amazon S3 bucket, AWS Lambda is automatically triggered to validate, clean, transform, and load the data into Amazon DynamoDB. The entire solution is designed using AWS managed services and can be integrated with a CI/CD workflow using GitHub and AWS CodePipeline.

---

# Architecture

```text
                        Developer
                            │
                            ▼
                     GitHub Repository
                            │
                  (Source Code Versioning)
                            │
                GitHub Actions (Optional)
                            │
                            ▼
                    AWS CodePipeline
                            │
                  Deploy Latest Lambda
                            │
                            ▼
                   AWS Lambda Function
                            ▲
                            │
            S3 ObjectCreated Event Trigger
                            ▲
                            │
      Upload CSV to weather-etl-manu/raw/
                            │
                            ▼
                    Amazon S3 Bucket
                            │
                            ▼
                  Extract CSV Records
                            │
                            ▼
               Validate & Transform Data
                            │
                            ▼
                 Amazon DynamoDB Table
                    (clean_records)
                            │
                            ▼
                  Amazon CloudWatch Logs
```

---

# Technology Stack

| Service           | Purpose                   |
| ----------------- | ------------------------- |
| AWS Lambda        | Serverless ETL processing |
| Amazon S3         | Raw CSV file storage      |
| Amazon DynamoDB   | Store transformed records |
| Amazon CloudWatch | Monitoring and logging    |
| AWS IAM           | Permissions management    |
| GitHub            | Source code repository    |
| GitHub Actions    | CI automation (optional)  |
| AWS CodePipeline  | Continuous deployment     |

---

# Project Workflow

```text
Developer Pushes Code
          │
          ▼
GitHub Repository
          │
          ▼
CodePipeline Deploys Lambda
          │
          ▼
Lambda Ready
          │
          ▼
Upload CSV to S3 raw/
          │
          ▼
S3 ObjectCreated Event
          │
          ▼
Lambda Triggered
          │
          ├── Extract CSV
          ├── Validate Records
          ├── Transform Data
          ├── Load into DynamoDB
          └── Write Audit Logs
                    │
                    ▼
              CloudWatch Logs
```

---

# Project Structure

```text
weather-etl/
│
├── lambda_function.py
├── sample_weather.csv
├── README.md
├── requirements.txt
└── .github/
    └── workflows/
        └── deploy.yml
```

---

# Step 1 – Create Amazon S3 Bucket

Created an S3 bucket to store raw weather CSV files.

Bucket Name

```
weather-etl-manu
```

Folder Structure

```
weather-etl-manu
│
├── raw/
│     ├── sample_weather.csv
│     └── sample_weather_v3.csv
│
└── processed/
```

Purpose

* Store incoming weather CSV files
* Trigger Lambda automatically on upload

---

# Step 2 – Create DynamoDB Table

Created a DynamoDB table to store cleaned records.

Table Name

```
clean_records
```

Partition Key

```
record_id (String)
```

Stored Attributes

* record_id
* city
* temperature
* humidity
* status
* processed_at

---

# Step 3 – Develop Lambda Function

Created Lambda Function

```
weather-etl
```

Runtime

```
Python 3.11
```

Responsibilities

* Read uploaded CSV
* Validate data
* Remove invalid records
* Standardize city names
* Convert numeric values
* Generate status
* Insert records into DynamoDB
* Generate audit logs

---

# ETL Logic

## Extract

Reads CSV from Amazon S3.

```python
response = s3_client.get_object(
    Bucket=bucket,
    Key=key
)
```

---

## Transform

Validation Rules

Required Fields

* record_id
* city
* temperature
* humidity

Temperature Range

```
-90°C to 60°C
```

Humidity Range

```
0% to 100%
```

Derived Field

```
Cold
Normal
Hot
```

Example

| Temperature | Status |
| ----------- | ------ |
| <15         | Cold   |
| 15–29.99    | Normal |
| ≥30         | Hot    |

---

## Load

Cleaned records are batch inserted into DynamoDB.

```python
table.batch_writer()
```

---

## Audit

Execution summary is written into CloudWatch.

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

# Step 4 – Configure Lambda Trigger

Added Amazon S3 Trigger.

Configuration

| Setting | Value            |
| ------- | ---------------- |
| Bucket  | weather-etl-manu |
| Event   | ObjectCreated    |
| Prefix  | raw/             |
| Suffix  | .csv             |

Result

Whenever a CSV is uploaded into

```
weather-etl-manu/raw/
```

Lambda executes automatically.

---

# Step 5 – Configure IAM Permissions

Execution Role

```
weather-etl-role
```

Attached Policies

* AWSLambdaBasicExecutionRole
* AmazonS3FullAccess
* AmazonDynamoDBFullAccess_v2

These permissions allow Lambda to

* Read S3 objects
* Write DynamoDB items
* Generate CloudWatch logs

---

# Step 6 – Upload CSV

Uploaded

```
sample_weather_v3.csv
```

Location

```
weather-etl-manu/raw/
```

This automatically generated an

```
ObjectCreated
```

event.

---

# Step 7 – Lambda Execution

CloudWatch Logs

```
Processing file:

s3://weather-etl-manu/raw/sample_weather_v3.csv
```

Audit Summary

```
Files Processed : 1

Total Records : 40

Inserted Records : 34

Rejected Records : 6
```

Execution completed successfully.

---

# Step 8 – Verify DynamoDB

Verified records inside

```
clean_records
```

Example

| record_id | city    | temperature | humidity | status |
| --------- | ------- | ----------- | -------- | ------ |
| 1010      | Mumbai  | 32.8        | 88       | Hot    |
| 1028      | Toronto | 12.1        | 57       | Cold   |
| 1037      | Chennai | 31.0        | 82       | Hot    |

---

# CloudWatch Monitoring

CloudWatch provides

* Lambda execution logs
* Error logs
* Processing summary
* Audit information

Example

```
Processing file:
sample_weather_v3.csv

Inserted Records:
34

Rejected Records:
6
```

---

# End-to-End Workflow

```text
Start
 │
 ▼
Developer Pushes Code
 │
 ▼
GitHub Repository
 │
 ▼
CodePipeline Deploys Lambda
 │
 ▼
Lambda Ready
 │
 ▼
Upload CSV to S3 raw/
 │
 ▼
S3 ObjectCreated Event
 │
 ▼
Lambda Triggered
 │
 ▼
Read CSV
 │
 ▼
Validate Data
 │
 ▼
Reject Invalid Records
 │
 ▼
Transform Records
 │
 ▼
Batch Insert into DynamoDB
 │
 ▼
Generate Audit Summary
 │
 ▼
CloudWatch Logs
 │
 ▼
End
```

---

# Project Outcome

Successfully implemented an event-driven serverless ETL pipeline that:

* Automatically detects new CSV uploads in Amazon S3.
* Validates and transforms weather records using AWS Lambda.
* Stores cleaned records in Amazon DynamoDB.
* Logs execution metrics and audit summaries in Amazon CloudWatch.
* Uses IAM roles to securely grant Lambda access to AWS resources.
* Can be integrated with GitHub and AWS CodePipeline for automated CI/CD deployments.

---

# Future Enhancements

* Add unit tests using `pytest`.
* Package and deploy Lambda automatically with GitHub Actions.
* Extend AWS CodePipeline with AWS CodeBuild for automated testing before deployment.
* Archive processed files to the `processed/` folder after successful execution.
* Add CloudWatch alarms and SNS notifications for failed ETL executions.
* Implement least-privilege IAM policies instead of full-access managed policies.
* Add dead-letter queues (DLQs) for failed Lambda invocations.
