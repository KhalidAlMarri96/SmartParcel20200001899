# -------------------------------------------------------
# SmartParcel — NET_214 Project, Spring 2026
# Author  : Khalid Ali
# ID      : 20200001899
# Email   : 20200001899@students.cud.ac.ae
# AWS Acc : 598892455787
# -------------------------------------------------------

from flask import Flask, request, jsonify
import uuid
import datetime
import socket
import boto3
import json

app = Flask(__name__)

# -------------------------
# AWS Configuration
# -------------------------
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
table = dynamodb.Table('smartparcel-parcels')

sqs = boto3.client('sqs', region_name='ap-southeast-2')
QUEUE_URL = "https://sqs.ap-southeast-2.amazonaws.com/598892455787/smartparcel-notifications-20200001899"

# -------------------------
# API KEY ROLES
# -------------------------
API_KEYS = {
    "admin-123": "admin",
    "driver-123": "driver",
    "customer-123": "customer"
}

VALID_STATUS = ["created", "picked_up", "in_transit", "delivered", "cancelled"]

# -------------------------
# HELPERS
# -------------------------
def get_user_role():
    key = request.headers.get("X-API-Key")
    if not key:
        return None, ("API key missing", 401)
    role = API_KEYS.get(key)
    if not role:
        return None, ("Invalid API key", 401)
    return role, None


def validate_body(fields):
    data = request.get_json(silent=True)
    if not data:
        return None, ("Invalid or missing JSON body", 400)
    for f in fields:
        if f not in data or not data[f]:
            return None, (f"{f} is required", 400)
    return data, None


def log_request(status):
    print(f"{datetime.datetime.utcnow()} | {request.method} {request.path} -> {status}")


# -------------------------
# HEALTH CHECK
# -------------------------
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "hostname": socket.gethostname()
    }), 200


# -------------------------
# CREATE PARCEL
# -------------------------
@app.route('/api/parcels', methods=['POST'])
def create_parcel():
    role, err = get_user_role()
    if err:
        return jsonify({"error": err[0]}), err[1]

    if role not in ["admin", "driver"]:
        return jsonify({"error": "Unauthorized"}), 403

    data, err = validate_body(["sender", "receiver", "address", "email"])
    if err:
        return jsonify({"error": err[0]}), err[1]

    parcel_id = f"PKG-{uuid.uuid4().hex[:8]}"

    item = {
        "parcel_id": parcel_id,
        "sender": data["sender"],
        "receiver": data["receiver"],
        "address": data["address"],
        "email": data["email"],
        "status": "created",
        "history": [
            {
                "status": "created",
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
        ]
    }

    table.put_item(Item=item)

    log_request(201)
    return jsonify({"parcel_id": parcel_id}), 201


# -------------------------
# GET PARCEL
# -------------------------
@app.route('/api/parcels/<parcel_id>', methods=['GET'])
def get_parcel(parcel_id):
    role, err = get_user_role()
    if err:
        return jsonify({"error": err[0]}), err[1]

    response = table.get_item(Key={"parcel_id": parcel_id})

    if "Item" not in response:
        return jsonify({"error": "Parcel not found"}), 404

    return jsonify(response["Item"]), 200


# -------------------------
# UPDATE STATUS
# -------------------------
@app.route('/api/parcels/<parcel_id>/status', methods=['PUT'])
def update_status(parcel_id):
    role, err = get_user_role()
    if err:
        return jsonify({"error": err[0]}), err[1]

    if role != "driver":
        return jsonify({"error": "Only drivers can update status"}), 403

    data, err = validate_body(["status"])
    if err:
        return jsonify({"error": err[0]}), err[1]

    new_status = data["status"]

    if new_status not in VALID_STATUS:
        return jsonify({"error": "Invalid status"}), 400

    res = table.get_item(Key={"parcel_id": parcel_id})

    if "Item" not in res:
        return jsonify({"error": "Parcel not found"}), 404

    parcel = res["Item"]

    if parcel["status"] == "cancelled":
        return jsonify({"error": "Cannot update cancelled parcel"}), 409

    # Update history
    parcel["history"].append({
        "status": new_status,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

    parcel["status"] = new_status

    table.put_item(Item=parcel)

    # -------------------------
    # SEND TO SQS (IMPORTANT)
    # -------------------------
    message = {
        "parcel_id": parcel_id,
        "new_status": new_status,
        "customer_email": parcel["email"],
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(message)
    )

    log_request(200)
    return jsonify({"message": "Status updated"}), 200


# -------------------------
# LIST PARCELS
# -------------------------
@app.route('/api/parcels', methods=['GET'])
def list_parcels():
    role, err = get_user_role()
    if err:
        return jsonify({"error": err[0]}), err[1]

    if role != "admin":
        return jsonify({"error": "Admin only"}), 403

    response = table.scan()
    return jsonify(response.get("Items", [])), 200


# -------------------------
# DELETE PARCEL
# -------------------------
@app.route('/api/parcels/<parcel_id>', methods=['DELETE'])
def delete_parcel(parcel_id):
    role, err = get_user_role()
    if err:
        return jsonify({"error": err[0]}), err[1]

    if role != "admin":
        return jsonify({"error": "Admin only"}), 403

    res = table.get_item(Key={"parcel_id": parcel_id})

    if "Item" not in res:
        return jsonify({"error": "Not found"}), 404

    parcel = res["Item"]

    if parcel["status"] != "created":
        return jsonify({"error": "Cannot cancel after pickup"}), 409

    parcel["status"] = "cancelled"
    table.put_item(Item=parcel)

    return jsonify({"message": "Parcel cancelled"}), 200


# -------------------------
# RUN APP
# -------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
