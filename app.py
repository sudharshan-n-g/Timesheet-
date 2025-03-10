from flask import Flask, request, jsonify
from pymongo import MongoClient
from Emp_timesheet import add_PM_data, delete_emp, add_AM_data, employee_login
from Emp_info import add_emp_info
from flask_cors import CORS
#from pyngrok import ngrok
import os

application = Flask(__name__)
##CORS(application) 
#CORS(application, resources={r"/*": {"origins": "*"}}) # Enable CORS for frontend-backend communication
#
## Start ngrok tunnel
port = 8000  # Set the same port as Flask
#public_url = ngrok.connect(port).public_url
#print(f"Ngrok Tunnel URL: {public_url}")

@application.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("email")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user_data = employee_login(username, password)  # Check credentials

    if user_data:
        return jsonify({"user": user_data, "message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401



@application.route("/add_timesheet", methods=["POST"])
def add_AM_timesheet():
    data = request.json
    add_AM_data(data)
    return jsonify({"message": "Timesheet added successfully"})

@application.route("/add_PM_timesheet", methods=["POST"])
def add_PM_timesheet():
    data = request.json
    add_PM_data(data)
    return jsonify({"message": "Timesheet added successfully"})

@application.route("/delete_employee", methods=["DELETE"])
def delete_employee():
    emp_name = request.json["employee_name"]
    delete_emp(emp_name)
    return jsonify({"message": "Employee deleted successfully"})

@application.route("/add_employee", methods=["POST"])  # Fixed: Added missing route
def add_employee():
    emp_name = request.json
    add_emp_info(emp_name)
    return jsonify({"message": "Employee added successfully"})

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=port)
