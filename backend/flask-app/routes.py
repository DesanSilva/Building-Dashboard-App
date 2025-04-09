import os
import json
import pytz
from datetime import datetime
from flask import Blueprint, jsonify, request
import boto3
from boto3.dynamodb.conditions import Key

api = Blueprint('api', __name__)

TOPIC_AC_CONTROL = os.environ.get("TOPIC_AC_CONTROL", "api/control/ac")
TOPIC_LIGHTS_CONTROL = os.environ.get("TOPIC_LIGHTS_CONTROL", "api/control/lights")
SENSOR_TABLE = os.environ.get("SENSOR_TABLE", "SensorData")
USER_INPUT_TABLE = os.environ.get("USER_INPUT_TABLE", "UserInputs")
AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")

class DeviceState:
    def __init__(self):
        self.ac_status = False
        self.lights_status = False

device_state = DeviceState()

def get_aws_clients():
    session = boto3.Session(region_name=AWS_REGION)
    iot_client = session.client('iot-data')
    dynamodb = session.resource('dynamodb')
    input_table = dynamodb.Table(USER_INPUT_TABLE)
    sensor_table = dynamodb.Table(SENSOR_TABLE)

    try:
        table_desc = sensor_table.meta.client.describe_table(TableName=SENSOR_TABLE)
        key_schema = table_desc['Table']['KeySchema']
        partition_key = next((item['AttributeName'] for item in key_schema if item['KeyType'] == 'HASH'), 'deviceId')
    except Exception as e:
        print(f"Error retrieving sensor_table schema: {e}")
        partition_key = 'deviceId'
        
    return iot_client, input_table, sensor_table, partition_key

#------------------------------------------------------------------------------------------------------------------------
@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

#------------------------------------------------------------------------------------------------------------------------
@api.route('/sensors', methods=['GET'])
def get_sensor_data():
    device_id = request.args.get('deviceId', 'esp32_01')
    try:
        _, _, table, partition_key = get_aws_clients()
        
        response = table.query(
            KeyConditionExpression=Key(partition_key).eq(device_id),
            ScanIndexForward=False,  # Descending order
            Limit=1
        )

        items = response.get('Items', [])
        if items:
            item = items[0]
            if "time" in item:
                iso_timestamp = item["time"]
                dt = datetime.fromisoformat(iso_timestamp)
                item["time"] = dt.strftime('%Y-%m-%d %H:%M:%S')
            return jsonify(item), 200
        else:
            return jsonify({
                "message": f"No data found for device {device_id}",
                "timestamp": datetime.now().isoformat()
            }), 404
        
    except Exception as e:
        print(f"Error in get_sensor_data: {str(e)}")
        return jsonify({
            "error": str(e),
            "message": "Failed to retrieve sensor data",
            "timestamp": datetime.now().isoformat()
        }), 500

#------------------------------------------------------------------------------------------------------------------------
@api.route('/control/ac', methods=['POST'])
def control_ac():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.json
    try:
        new_status = data.get('status', False)
        device_state.ac_status = new_status
        iso8601_time = datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()
        
        message = {
            "device": "ac",
            "status": new_status,
            "timestamp": datetime.now().isoformat()
        }
        
        iot_client, table, _, _ = get_aws_clients()
        
        iot_client.publish(
            topic=TOPIC_AC_CONTROL,
            qos=1,
            payload=json.dumps(message)
        )
        
        table.put_item(Item={
            "device": "ac",
            "time": iso8601_time,
            "status": new_status
        })
 
        return jsonify({
            "success": True, 
            "message": f"AC turned {'on' if new_status else 'off'}",
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Error in control_ac: {str(e)}")
        return jsonify({
            "success": False, 
            "message": f"Error controlling AC: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

#------------------------------------------------------------------------------------------------------------------------
@api.route('/control/lights', methods=['POST'])
def control_lights():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.json
    try:
        new_status = data.get('status', False)
        device_state.lights_status = new_status
        iso8601_time = datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()
            
        message = {
            "device": "lights",
            "status": new_status,
            "timestamp": datetime.now().isoformat()
        }
        
        iot_client, table, _, _ = get_aws_clients()
        
        iot_client.publish(
            topic=TOPIC_LIGHTS_CONTROL,
            qos=1,
            payload=json.dumps(message)
        )
        
        table.put_item(Item={
            "device": "lights",
            "time": iso8601_time,
            "status": new_status
        })
        
        return jsonify({
            "success": True, 
            "message": f"Lights turned {'on' if new_status else 'off'}",
            "timestamp": datetime.now().isoformat()
        }), 200
            
    except Exception as e:
        print(f"Error in control_lights: {str(e)}")
        return jsonify({
            "success": False, 
            "message": f"Error controlling lights: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500