import json
from pymongo import MongoClient
from mail import review_performance
from werkzeug.security import check_password_hash

def add_new_user(user_input):
    client = MongoClient("mongodb+srv://prashitar:Vision123@cluster0.v7ckx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["Timesheet"]
    collection_emp = db["Employee_credentials"]
    collection_admin = db["Admin_credentials"]
    if user_input["role"] == "admin":
        result = collection_admin.insert_one(user_input)
    else:
        result = collection_emp.insert_one(user_input)

def delete_emp(emp_name):
    client = MongoClient("mongodb+srv://prashitar:Vision123@cluster0.v7ckx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["Timesheet"]
    collection = db["Employee_data"]
    collection_AM =db["Employee_AM"]
    collection_PM =db["Employee_PM"]
    result = collection.delete_one({"employee_name": emp_name})
    collection_AM.delete_many({"employee_name": emp_name})
    collection_PM.delete_many({"employee_name": emp_name})

def get_emp_data(emp_name,date):
    client = MongoClient("mongodb+srv://prashitar:Vision123@cluster0.v7ckx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["Timesheet"]
    collection = db["Employee_PM"]
    emp_data = collection.find_one({"employee_name": emp_name, "date": date})
    return emp_data




