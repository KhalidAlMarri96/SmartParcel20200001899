import json
import boto3
import os

sns = boto3.client("sns")

TOPIC_ARN = os.environ["TOPIC_ARN"]

def lambda_handler(event, context):
    for record in event["Records"]:
        body = json.loads(record["body"])

        parcel_id = body.get("parcel_id")
        new_status = body.get("new_status")
        customer_email = body.get("customer_email")
        driver_name = body.get("driver_name", "Driver")
        timestamp = body.get("timestamp")
        photo_url = body.get("photo_url", "N/A")

        message = (
            f"SmartParcel update\n\n"
            f"Parcel ID: {parcel_id}\n"
            f"New Status: {new_status}\n"
            f"Customer Email: {customer_email}\n"
            f"Driver: {driver_name}\n"
            f"Time: {timestamp}\n"
            f"Photo: {photo_url}"
        )

        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject=f"SmartParcel Update: {parcel_id}",
            Message=message
        )

        print(f"Notification sent for {parcel_id}")

    return {
        "statusCode": 200,
        "body": json.dumps("Done")
    }
