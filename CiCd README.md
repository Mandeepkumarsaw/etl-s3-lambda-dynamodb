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












# AWS Serverless ETL Pipeline with CI/CD

A production-ready **Serverless ETL (Extract, Transform, Load) Pipeline** built using **AWS Lambda, Amazon S3, Amazon DynamoDB**, and automated through a complete **CI/CD pipeline** using **GitHub, AWS CodePipeline, and AWS CodeBuild**.

---

# Project Overview

This project automatically processes weather datasets uploaded to Amazon S3.

The ETL workflow performs:

- Extract weather CSV data from Amazon S3
- Validate and clean records
- Transform data into a standardized format
- Load processed records into Amazon DynamoDB
- Archive processed files back to Amazon S3
- Automatically deploy new Lambda code using CI/CD whenever changes are pushed to GitHub

---

# Architecture

```
                     GitHub Repository
                            │
                     (Push Source Code)
                            │
                            ▼
                   AWS CodePipeline
                            │
          ┌─────────────────┴─────────────────┐
          │                                   │
      Source Stage                      Build Stage
       (GitHub)                        (CodeBuild)
                                              │
                                              ▼
                                   Build using buildspec.yml
                                              │
                                              ▼
                                       Deploy Stage
                                        AWS Lambda
                                              │
                                              ▼
                                    Weather ETL Function
                                              │
                          Reads CSV files from Amazon S3
                                              │
                                              ▼
                               Cleans & Transforms Data
                                              │
                                              ▼
                          Stores Processed Data in DynamoDB
                                              │
                                              ▼
                               Archives Output to Amazon S3
```

---

# Existing ETL Infrastructure

The following AWS resources were already implemented before adding CI/CD.

## AWS Lambda

- Weather ETL Lambda Function

Responsibilities:

- Read CSV files
- Validate records
- Clean missing values
- Transform weather data
- Load into DynamoDB
- Archive processed files

---

## Amazon S3

Bucket Structure

```
weather-data-bucket/

raw/

processed/

archive/
```

Purpose

- Store raw CSV files
- Store processed files
- Trigger Lambda automatically

---

## Amazon DynamoDB

Stores processed weather records.

Example attributes

- City
- Date
- Temperature
- Humidity
- Wind Speed
- AQI
- Timestamp

---

## IAM Role

Lambda Execution Role

```
weather-etl-role-ligw0jxq
```

Provides permissions to

- Read S3
- Write DynamoDB
- Create CloudWatch Logs

---

## Source Code

```
lambda_function.py
requirements.txt
```

---

# CI/CD Implementation

To automate deployments, the following resources were added.

---

# 1. GitHub Repository

Created GitHub repository

```
etl-s3-lambda-dynamodb
```

Repository Structure

```
etl-s3-lambda-dynamodb/

│── lambda_function.py
│── requirements.txt
│── buildspec.yml
│── .gitignore
│── README.md
```

Git Commands Used

```bash
git init

git add .

git commit -m "Initial Commit"

git remote add origin https://github.com/<username>/etl-s3-lambda-dynamodb.git

git push origin main
```

---

# 2. S3 Artifact Bucket

Created an S3 bucket to store CodePipeline artifacts.

Purpose

- Source artifact
- Build artifact
- Deployment package

---

# 3. CodeBuild Project

Created CodeBuild Project

```
weather-etl-build-cicd
```

Purpose

- Download source code
- Install dependencies
- Validate project
- Package Lambda
- Generate deployment artifact

---

# 4. CodeBuild Service Role

Created IAM Role

```
codebuild-weather-etl-build-cicd-service-role
```

Permissions

- Amazon S3
- CloudWatch Logs
- Lambda
- CodeBuild

---

# 5. Build Specification

Created

```
buildspec.yml
```

Example

```yaml
version: 0.2

phases:

  install:
    runtime-versions:
      python: 3.11

  build:
    commands:
      - echo Build Started
      - pip install -r requirements.txt -t package
      - cp lambda_function.py package/
      - cd package
      - zip -r ../lambda.zip .

artifacts:
  files:
    - lambda.zip
```

---

# 6. GitHub Connection

Connected GitHub with AWS.

Connection Type

```
GitHub (OAuth App)
```

Purpose

Allows CodePipeline to access the GitHub repository.

---

# 7. AWS CodePipeline

Created Pipeline

```
weather-etl-pipeline
```

Stages

```
Source

↓

Build

↓

Deploy
```

---

## Source Stage

Provider

```
GitHub (OAuth App)
```

Branch

```
main
```

Automatically detects new commits.

---

## Build Stage

Provider

```
AWS CodeBuild
```

Project

```
weather-etl-build-cicd
```

Reads

```
buildspec.yml
```

Packages Lambda.

---

## Deploy Stage

Provider

```
AWS Lambda
```

Deploys latest build directly to

```
weather-etl
```

---

# 8. CodePipeline Service Role

Automatically created

```
AWSCodePipelineServiceRole-ap-southeast-2-weather-etl-pipeline
```

Responsibilities

- Access GitHub
- Trigger CodeBuild
- Deploy Lambda

---

# 9. CloudWatch Logs

Automatically created log groups

```
/aws/codebuild/weather-etl-build-cicd
```

Used for

- Build logs
- Error debugging
- Monitoring

---

# Complete CI/CD Workflow

```
Developer

     │

git add

git commit

git push

     │

     ▼

GitHub Repository

     │

     ▼

AWS CodePipeline

     │

     ▼

Source Stage

     │

     ▼

AWS CodeBuild

     │

     ▼

Install Dependencies

     │

     ▼

Package Lambda

     │

     ▼

Deploy Stage

     │

     ▼

AWS Lambda

     │

     ▼

Updated ETL Pipeline
```

---

# AWS Resources Used

## Existing ETL Resources

| Service | Resource |
|----------|----------|
| AWS Lambda | Weather ETL Function |
| Amazon S3 | Raw & Processed Data Bucket |
| Amazon DynamoDB | Weather Data Table |
| IAM | Lambda Execution Role |
| CloudWatch | Lambda Logs |

---

## CI/CD Resources Created

| Service | Resource |
|----------|----------|
| GitHub | etl-s3-lambda-dynamodb Repository |
| Amazon S3 | Pipeline Artifact Bucket |
| AWS CodeBuild | weather-etl-build-cicd |
| IAM | codebuild-weather-etl-build-cicd-service-role |
| AWS CodePipeline | weather-etl-pipeline |
| IAM | AWSCodePipelineServiceRole-ap-southeast-2-weather-etl-pipeline |
| CloudWatch | CodeBuild Log Group |
| GitHub Connection | OAuth Connection |
| Build Specification | buildspec.yml |

---

# Repository Structure

```
etl-s3-lambda-dynamodb/

├── lambda_function.py
├── requirements.txt
├── buildspec.yml
├── .gitignore
├── README.md
```

---

# CI/CD Benefits

- Fully automated deployment
- Version-controlled source code
- Continuous Integration
- Continuous Delivery
- Automatic build verification
- Faster deployments
- Improved collaboration
- Easy rollback using Git history
- Centralized monitoring with CloudWatch Logs

---

# End-to-End Workflow

1. Developer updates the Lambda source code.
2. Changes are committed and pushed to the `main` branch on GitHub.
3. AWS CodePipeline detects the new commit automatically.
4. The Source stage retrieves the latest code from GitHub.
5. AWS CodeBuild installs dependencies and packages the Lambda function using `buildspec.yml`.
6. The packaged artifact is passed to the Deploy stage.
7. AWS Lambda is updated with the latest version of the code.
8. The updated ETL pipeline processes newly uploaded weather CSV files from Amazon S3.
9. Processed data is stored in Amazon DynamoDB, and execution logs are available in Amazon CloudWatch.

---

# Future Enhancements

- Add automated unit testing before deployment.
- Configure deployment approvals for production releases.
- Add SNS notifications for pipeline failures.
- Use AWS SAM or CloudFormation for Infrastructure as Code (IaC).
- Implement multi-environment deployments (Development, Staging, Production).

---

# Author

**Mandeep Kumar Saw**

AWS | Python | Serverless | ETL | DevOps | CI/CD
