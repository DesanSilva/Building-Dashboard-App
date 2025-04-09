import json
import boto3
from datetime import datetime
import pytz

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('SensorData')

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    try:
        sensor_time = event.get("time")
        local_time = datetime.strptime(sensor_time, '%Y-%m-%d %H:%M:%S')
        local_time_with_tz = pytz.timezone('Asia/Kolkata').localize(local_time)
        iso8601_time = local_time_with_tz.isoformat()
        
    except Exception as e:
        print(f"Error converting time to UTC: {e}")
        iso8601_time = datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()


    readings = {
        "deviceId": event.get("mqttMetadata", {}).get("clientId", "esp32_01"),
        "time": iso8601_time,
        "temperature": event.get("temperature", None),
        "humidity": event.get("humidity", None),
        "luminance": event.get("luminance", None)
    }

    try:
        response = table.put_item(Item=readings)
        print("Data successfully written to DynamoDB:", response)

        return {
            'statusCode': 200,
            'body': json.dumps('Data successfully saved!')
        }

    except Exception as e:
        print(f"Error writing to DynamoDB: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Failed to save data.')
        }
