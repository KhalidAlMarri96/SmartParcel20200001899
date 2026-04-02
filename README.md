SmartParcel20200001899
SmartParcel is a cloud-native parcel tracking system built for the NET_214 Network Programming project.

Student Information
Student Name: Khalid Al Marri
Student ID: 20200001899
Course: NET_214 — Network Programming
Semester: Spring 2026

Project Description
This project is a parcel tracking API built with Python Flask and deployed on AWS EC2.
It supports parcel creation, parcel tracking, status updates, cancellation, health check, and concurrent request handling.

Main Features
Create a parcel
Get parcel details
Update parcel status
List parcels
Cancel a parcel
Health check endpoint
Basic API key authentication
Concurrent handling using Flask/Gunicorn
AWS integration for cloud deployment

Files
app.py -> main Flask application
lab_test.py -> test script
README.md -> project setup and usage instructions

Requirements
Python 3
Flask
Requests
boto3
gunicorn

Install Dependencies
pip install flask requests boto3 gunicorn

Run the Application Locally
python3 app.py

Run with Gunicorn
gunicorn --bind 0.0.0.0:8080 --workers 4 --threads 2 app:app

Example Endpoints
Health Check:
curl http://<EC2-PUBLIC-IP>:8080/health

Create Parcel:
curl -X POST http://<EC2-PUBLIC-IP>:8080/api/parcels \
  -H "Content-Type: application/json" \
  -H "X-API-Key: key-driver-001" \
  -d '{"sender":"Ali","receiver":"Sara","address":"Dubai","email":"sara@example.com"}'

Get Parcel:
curl -H "X-API-Key: key-customer-001" \
  http://<EC2-PUBLIC-IP>:8080/api/parcels/<parcel_id>

Notes
Replace <EC2-PUBLIC-IP> with the public IP of the AWS EC2 instance.
Replace <parcel_id> with a real parcel ID returned by the API.
AWS services such as S3, DynamoDB, SQS, Lambda, and SNS can be connected based on deployment setup.
EOF
