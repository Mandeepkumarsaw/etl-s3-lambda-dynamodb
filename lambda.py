"""
lambda_function.py
-------------------
Serverless ETL handler for the Weather ETL use case.

Trigger    : S3 ObjectCreated event on the `raw/` prefix (CSV files)
Extract    : Read raw CSV file from Amazon S3
Transform  : Validate, clean, standardize, and enrich records
Load       : Store cleaned records into DynamoDB
Audit      : Log ETL summary to CloudWatch
"""

import csv
import io
import json
import logging
import os
from datetime import datetime, timezone
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

# -----------------------------------------------------------------------------
# AWS Clients
# -----------------------------------------------------------------------------
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "clean_records")

table = dynamodb.Table(TABLE_NAME)

# -----------------------------------------------------------------------------
# Validation Rules
# -----------------------------------------------------------------------------
REQUIRED_FIELDS = [
    "record_id",
    "city",
    "temperature",
    "humidity",
]

MIN_TEMP = -90.0
MAX_TEMP = 60.0

MIN_HUMIDITY = 0
MAX_HUMIDITY = 100


# -----------------------------------------------------------------------------
# Lambda Handler
# -----------------------------------------------------------------------------
def lambda_handler(event, context):

    summary = {
        "files_processed": 0,
        "total_input_records": 0,
        "inserted_records": 0,
        "rejected_records": 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    for record in event.get("Records", []):

        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"].replace("+", " ")

        logger.info("Processing file : s3://%s/%s", bucket, key)

        rows = extract(bucket, key)

        clean_records, rejected = transform(rows)

        inserted = load(clean_records)

        summary["files_processed"] += 1
        summary["total_input_records"] += len(rows)
        summary["inserted_records"] += inserted
        summary["rejected_records"] += rejected

    audit(summary)

    return {
        "statusCode": 200,
        "body": summary
    }


# -----------------------------------------------------------------------------
# EXTRACT
# -----------------------------------------------------------------------------
def extract(bucket, key):
    """
    Read CSV file from Amazon S3.
    """

    response = s3_client.get_object(
        Bucket=bucket,
        Key=key
    )

    csv_content = response["Body"].read().decode("utf-8")

    return list(csv.DictReader(io.StringIO(csv_content)))


# -----------------------------------------------------------------------------
# TRANSFORM
# -----------------------------------------------------------------------------
def transform(rows):
    """
    Transformation Rules

    1. Remove invalid records
    2. Standardize city names
    3. Convert temperature & humidity
    4. Add derived field : status
    """

    clean_records = []
    rejected = 0

    for row in rows:

        validated = validate(row)

        if validated is None:
            rejected += 1
            continue

        temperature, humidity = validated

        clean_records.append(
            {
                "record_id": row["record_id"].strip(),
                "city": row["city"].strip().title(),
                "temperature": Decimal(str(round(temperature, 2))),
                "humidity": Decimal(str(round(humidity, 2))),
                "status": derive_status(temperature),
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    return clean_records, rejected


# -----------------------------------------------------------------------------
# VALIDATE
# -----------------------------------------------------------------------------
def validate(row):

    for field in REQUIRED_FIELDS:
        if not str(row.get(field, "")).strip():
            return None

    try:
        temperature = float(row["temperature"])
        humidity = float(row["humidity"])
    except (TypeError, ValueError):
        return None

    if not (MIN_TEMP <= temperature <= MAX_TEMP):
        return None

    if not (MIN_HUMIDITY <= humidity <= MAX_HUMIDITY):
        return None

    return temperature, humidity


# -----------------------------------------------------------------------------
# DERIVED FIELD
# -----------------------------------------------------------------------------
def derive_status(temp):

    if temp < 15:
        return "Cold"

    if temp < 30:
        return "Normal"

    return "Hot"


# -----------------------------------------------------------------------------
# LOAD
# -----------------------------------------------------------------------------
def load(clean_records):
    """
    Write cleaned records into DynamoDB.
    """

    inserted = 0

    with table.batch_writer(overwrite_by_pkeys=["record_id"]) as batch:

        for item in clean_records:

            try:
                batch.put_item(Item=item)
                inserted += 1

            except ClientError as error:
                logger.error(
                    "Failed to insert %s : %s",
                    item["record_id"],
                    error
                )

    return inserted


# -----------------------------------------------------------------------------
# AUDIT
# -----------------------------------------------------------------------------
def audit(summary):
    """
    Log ETL summary to CloudWatch.
    """

    logger.info(json.dumps({"audit_summary": summary}))