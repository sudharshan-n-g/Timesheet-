import json
from pymongo import MongoClient
from mail import review_performance
from werkzeug.security import check_password_hash

def employee_login(emp_name,emp_password):
    client = MongoClient("mongodb+srv://prashitar:Vision123@cluster0.v7ckx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["Timesheet"]
    collection = db["Employee_credentials"]
    user = collection.find_one({"Username": emp_name}) 
    
    #for data in user:
    username = user["Username"]
    password = user["Password"]
    if username==emp_name and password==emp_password:

    #if user and check_password_hash(user["Password"], emp_password):  # Verify hashed password
        return {"Username": user["Username"], "message": "Login successful"}
    
    else:
        return None

def get_manager_details(emp_name):
    client = MongoClient("mongodb+srv://prashitar:Vision123@cluster0.v7ckx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["Timesheet"]
    collection = db["Employee_data"]

    data = collection.find({"fullName":emp_name})

    for value in data:
        manager = value["managerName"]
        mail = value["managerEmail"]
    return manager,mail


def add_PM_data(user_input):
    client = MongoClient("mongodb+srv://prashitar:Vision123@cluster0.v7ckx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["Timesheet"]
    collection = db["Employee_PM"]

    
    result = collection.insert_one(user_input)

    emp_name = user_input["employee_name"]
    manager, mail = get_manager_details(emp_name)
    
    review_performance(user_input,manager,mail)
 
    print(f"Data inserted with record id: {result.inserted_id}")


def add_AM_data(user_input):
    client = MongoClient("mongodb+srv://prashitar:Vision123@cluster0.v7ckx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    print("connected")
    db = client["Timesheet"]
    collection = db["Employee_AM"]
    
    result = collection.insert_one(user_input)
    print(f"Data inserted with record id: {result.inserted_id}")

def delete_emp(emp_name):
    client = MongoClient("mongodb+srv://prashitar:Vision123@cluster0.v7ckx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["Timesheet"]
    collection = db["Employee_data"]
    collection_AM =db["Employee_AM"]
    collection_PM =db["Employee_PM"]
    result = collection.delete_one({"employee_name": emp_name})
    collection_AM.delete_many({"employee_name": emp_name})
    collection_PM.delete_many({"employee_name": emp_name})
    

# Prompt the user for the timesheet JSON
#user_input_PM = {
#  "employee_name": "Sudharshan",
#  "date": "2025-02-20",
#  "hours": [
#    {
#      "hour": "08:00-09:00",
#      "task": "Annotations",
#      "progress": "green",
#      "comments": "Completed successfully"
#      
#    },
#    {
#      "hour": "09:00-10:00",
#      "task": "Model building and training",
#      "progress": "yellow",
#      "comments": "In progress"
#    },
#    {
#      "hour": "10:00-11:00",
#      "task": "Model testing",
#      "progress": "red",
#      "comments": "Blocked by dependencies"
#    }
#  ],
#  "Performance of the Day" : "green",
#  "First Time Quality" : "red",
#  "On-Time Delivery" : "red",
#  "Engagement and Support" : "red"
#}
#
#user_input_AM = {
#  "employee_name": "Sudharshan",
#  "date": "2025-02-20",
#  "hours": [
#    {
#      "hour": "08:00-09:00",
#      "task": "Annotations"
#    },
#    {
#      "hour": "09:00-10:00",
#      "task": "Model building and training"
#    },
#    {
#      "hour": "10:00-11:00",
#      "task": "Model testing"
#    }
#  ]
#}
#
#add_AM_data(user_input_PM)

#print(get_manager_details("Sudharshan"))

#result = employee_login("bhargav","BNG")
#print(result)