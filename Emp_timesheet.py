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


def employee_login(emp_name,emp_password):
    client = MongoClient("mongodb+srv://prashitar:Vision123@cluster0.v7ckx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["Timesheet"]
    collection = db["Employee_credentials"]
    user = collection.find_one({"Username": emp_name}) 
    
    #for data in user:
    username = user["Username"]
    password = user["Password"]
    if username==emp_name and password==emp_password:
        if username=="admin":
    #if user and check_password_hash(user["Password"], emp_password):  # Verify hashed password
            return {"Username": user["Username"], "message": "Admin login successful"}
        else:
            return {"Username":user["Username"],"message":"Login successful"}
    
    
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


def add_AM_data(data):
    client = MongoClient("mongodb+srv://prashitar:Vision123@cluster0.v7ckx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["Timesheet"]
    collection = db["Employee_AM"]

    # Extract the first valid hour from "tasks" (not "hours")
    first_am_hour = next(
        (hour for hour, details in data.get("tasks", {}).items() if details.get("description")),
        None
    )

    # Determine shift based on first valid hour
    if first_am_hour:
        shift = "USD" if first_am_hour.startswith("8") else "IND"
    else:
        shift = "UNKNOWN"  # Default shift if no valid hour is found

    # Format hours list
    formatted_hours = [
        {"hour": hour, "task": details["description"]}
        for hour, details in data.get("tasks", {}).items() if details["description"]
    ]

    # Create the final formatted document
    formatted_data = {
        "employee_name": data.get("employee_name"),
        "date": data.get("date"),
        "hours": formatted_hours,
        "shift": shift  # Add shift field
    }

    # Insert into MongoDB
    result = collection.insert_one(formatted_data)
    print(f"AM Data inserted with record id: {result.inserted_id}")


def add_PM_data(data):
    client = MongoClient("mongodb+srv://prashitar:Vision123@cluster0.v7ckx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["Timesheet"]
    collection = db["Employee_PM"]

    # Extract the first valid hour
    first_pm_hour = next(
        (hour for hour, details in data.get("hours", {}).items() if details.get("description")),
        None
    )

    # Determine shift based on first valid hour
    shift = "USD" if first_pm_hour and first_pm_hour.startswith("8") else "IND"

    # Format hours list
    formatted_hours = [
        {
            "hour": hour,
            "task": details["description"],
            "progress": details.get("status", "green").lower(),
            "comments": details.get("comment", "")
        }
        for hour, details in data.get("hours", {}).items() if details.get("description")
    ]

    # Create the final formatted document
    formatted_data = {
        "employee_name": data.get("employee_name"),
        "date": data.get("date"),
        "hours": formatted_hours,
        "shift": shift,  # Add shift field
        "country": data.get("country")
    }

    # Insert into MongoDB (Overwrite if employee & date exist)
    filter_condition = {
        "employee_name": formatted_data["employee_name"],
        "date": formatted_data["date"]
    }
    result = collection.update_one(
        filter_condition, 
        {"$set": formatted_data}, 
        upsert=True  # Overwrite if exists, insert if not
    )

    if result.matched_count > 0:
        print(f"Updated existing PM data for {formatted_data['employee_name']} on {formatted_data['date']}")
    else:
        print(f"Inserted new PM data for {formatted_data['employee_name']} on {formatted_data['date']}")

def performance_matrices(email, date, ratings):
    client = MongoClient("mongodb+srv://prashitar:Vision123@cluster0.v7ckx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["Timesheet"]
    collection = db["Employee_PM"]
    print(ratings)

    # Update the document where email and date match
    result = collection.update_one(
        {"employee_name": email, "date": date},  # Match condition
        {"$set": {"ratings": ratings}}  # Update or insert the ratings field
    )
    emp_name = email
    manager, mail = get_manager_details(emp_name)
    user_input = collection.find_one({"employee_name": email, "date": date})
    review_performance(user_input,manager,mail)

    



