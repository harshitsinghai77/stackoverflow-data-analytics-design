import requests
import datetime
import json

import boto3

# set up S3 client
s3 = boto3.client("s3")


def lambda_handler(event, context):

    try:
        # API endpoint for StackOverflow
        api_endpoint = "https://api.stackexchange.com/2.3/tags?order=desc&sort=popular&site=stackoverflow"
        # or           'https://api.stackexchange.com/2.3/questions?order=desc&sort=activity&site=stackoverflow'

        # Send GET request to the API endpoint
        response = requests.get(api_endpoint)

        if response.status_code != 200:
            raise ValueError(f"Request failed with error code {response.status_code}")

        # get the current timestamp
        current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        year, month, day = current_time.split("-")[:3]

        # Define the S3 bucket and key
        s3_file_name = f"questions_raw/{year}/{month}/{day}/stackoverflow_raw_data_{current_time}.json"
        s3_bucket_name = "stackoverflow-raw-bucket"

        # upload the content to S3 bucket
        s3.put_object(Bucket=s3_bucket_name, Key=s3_file_name, Body=response.content)

        return {"statusCode": 200, "body": "Data fetched and saved to S3 bucket"}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps(f"Error: {str(e)}")}
