import json
from pymongo import MongoClient
from mail import review_performance
from werkzeug.security import check_password_hash

def convert_to_time_range(time_str):
    from datetime import datetime, timedelta
    
    try:
        start_time = datetime.strptime(time_str, "%I:%M %p")
        end_time = start_time + timedelta(hours=1)
        return f"{start_time.strftime('%I:%M')}-{end_time.strftime('%I:%M')}"
    except ValueError:
        return time_str  # Return as-is if format is unexpected


def transform_timesheet(data):
    transformed_data = {
        "employee_name": data["employee_name"],
        "date": data["date"],
        "hours": []
    }

    for hour, details in data["hours"].items():
        if details["description"].strip():  # Ignore empty descriptions
            transformed_data["hours"].append({
                "hour": convert_to_time_range(hour),
                "task": details["description"],
                "progress": details.get("status", "Not Set"),
                "comments": details.get("comment", "")
            })

    return transformed_data

def add_new_user(user_input):
    client = MongoClient("mongodb+srv://prashitar:Vision123@cluster0.v7ckx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["Timesheet"]
    collection_emp = db["Employee_credentials"]
    collection_admin = db["Admin_credentials"]
    if user_input["role"] == "admin":
        result = collection_admin.insert_one(user_input)
    else:
        result = collection_emp.insert_one(user_input)

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


def add_PM_data(data):
    client = MongoClient("mongodb+srv://prashitar:Vision123@cluster0.v7ckx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["Timesheet"]
    collection = db["Employee_PM"]
    hours_list = []
    transformed_data = transform_timesheet(data)
    #for hour, task in data.get("tasks", {}).items():
    #    if task.get("description"):  # Ensure task is not empty
    #        hours_list.append({
    #            "hour": hour,  # Keep the original time format
    #            "task": task["description"],
    #            "progress": task.get("status", "").lower(),  # Default to empty if status is missing
    #            "comments": task.get("comment", "")  # Default to empty string if no comment
    #        })
#
    ## Format final data for MongoDB insertion
    #user_input = {
    #    "employee_name": data.get("employee_name"),
    #    "date": data.get("date"),
    #    "hours": hours_list,  # Ensure hours are correctly populated
    #    "country": data.get("country")
    #}

    # Debugging output: Print data before inserting
    #print("Formatted Data Before Insertion:", data)

    # Insert into MongoDB
    result = collection.insert_one(transformed_data)

    
    

    #emp_name = user_input["employee_name"]
    #manager, mail = get_manager_details(emp_name)
    
    #review_performance(user_input,manager,mail)
 
   # print(f"Data inserted with record id: {result.inserted_id}")


def add_AM_data(data):
    client = MongoClient("mongodb+srv://prashitar:Vision123@cluster0.v7ckx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    #print("connected")
    db = client["Timesheet"]
    collection = db["Employee_AM"]
    formatted_hours = [
        {"hour": hour, "task": details["description"]}
        for hour, details in data.get("tasks", {}).items() if details["description"]
    ]

    # Create the final formatted document
    formatted_data = {
        "employee_name": data.get("employee_name"),
        "date": data.get("date"),
        "hours": formatted_hours
    }
    result = collection.insert_one(formatted_data)
    print(f"Data inserted with record id: {result.inserted_id}")

def performance_matrices(email, date, ratings):
    client = MongoClient("mongodb+srv://prashitar:Vision123@cluster0.v7ckx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["Timesheet"]
    collection = db["Employee_PM"]
    

    # Update the document where email and date match
    result = collection.update_one(
        {"employee_name": email, "date": date},  # Match condition
        {"$set": {"ratings": ratings}}  # Update or insert the ratings field
    )
    emp_name = email
    manager, mail = get_manager_details(emp_name)
    user_input = collection.find_one({"employee_name": email, "date": date})
    review_performance(user_input,manager,mail)

    

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
#  ]
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

#input_data = {
#    "employee_name": "bhargav",
#    "date": "2025-03-12",
#    "hours": {
#        "8:00 AM": {"description": "AUGMENTATION", "status": "Green"},
#        "9:00 AM": {"description": "MODEL BUILDING ", "comment": "NOT COMPLETED", "status": "Red"},
#        "10:00 AM": {"description": ""},
#        "11:00 AM": {"description": ""},
#        "12:00 PM": {"description": ""},
#        "1:00 PM": {"description": ""},
#        "2:00 PM": {"description": ""},
#        "3:00 PM": {"description": ""},
#        "4:00 PM": {"description": ""},
#        "5:00 PM": {"description": ""}
#    },
#    "country": "USA"
#}
#add_PM_data(input_data)

#print(get_manager_details("Sudharshan"))

#result = employee_login("bhargav","BNG")
#print(result)

#performance_matrices("Sudharshan","2025-02-20",{"Performance of the Day": "green", "First Time Quality": "red", "On-Time Delivery": "red", "Engagement and Support": "red"})