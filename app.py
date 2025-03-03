from flask import Flask, request, jsonify
from pymongo import MongoClient
from Emp_timesheet import add_PM_data, delete_emp,add_AM_data
from Emp_info import add_emp_info

application = Flask(__name__)

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

def add_empoyee():
    emp_name = request.json
    add_emp_info(emp_name)
    return jsonify({"message": "Employee added successfully"})


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000)
