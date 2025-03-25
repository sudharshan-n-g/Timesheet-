from pymongo import MongoClient
from collections import OrderedDict
from datetime import datetime

def add_project(project):
    client = MongoClient("mongodb+srv://prashitar:Vision123@cluster0.v7ckx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["Timesheet"]
    collection = db["Projects"]
    collection.insert_one(project)
    

def get_project_list():
    client = MongoClient("mongodb+srv://prashitar:Vision123@cluster0.v7ckx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["Timesheet"]
    collection = db["Projects"]  # Change to your collection name

    query = {}
    projection = {"_id": 0, "projectName": 1}
    
    # Fetch the data
    results = list(collection.find(query, projection))
    
    # Extract only project names into a list
    project_names = [proj["projectName"] for proj in results]

    return project_names

def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%m-%d-%y")
    except (ValueError, TypeError):
        return date_str  # If the format is incorrect or None, return as is


def retrieve_project():
    client = MongoClient("mongodb+srv://prashitar:Vision123@cluster0.v7ckx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["Timesheet"]
    collection = db["Projects"]
    project_details = collection.find({}, {"_id": 0, "projectName": 1, "projectNumber": 1, "startDate": 1, "endDate": 1})
    
    
    ordered_projects = [
        OrderedDict([
            ("projectNumber", project["projectNumber"]),
            ("projectName", project["projectName"]),
            ("startDate", format_date(project["startDate"])),
            ("endDate", format_date(project["endDate"]))
        ])
        for project in project_details
    ]
    #print(ordered_projects)

    return ordered_projects

def get_designation(employee_name):
    print(employee_name)
    client = MongoClient("mongodb+srv://prashitar:Vision123@cluster0.v7ckx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["Timesheet"]
    collection = db["Employee_data"]

    data = collection.find({"name":employee_name})

    for value in data:
        designation = value["designation"]

    return designation


def get_project_hours_pm(project_name):
    client = MongoClient("mongodb+srv://prashitar:Vision123@cluster0.v7ckx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["Timesheet"]
    collection_pm = db["Employee_PM"]


    try:
        pipeline = [
            {
                "$unwind": "$hours"  # Flatten the hours array
            },
            {
                "$match": {
                    "hours.projectName": project_name  # Filter by project
                }
            },
            {
                "$group": {
                    "_id": "$employee_name",  # Group by employee
                    "total_hours": {"$sum": 1}  # Count total hours spent
                }
            }
        ]

        pm_data = list(collection_pm.aggregate(pipeline))

        # List of employees and their hours
        employees_list = [
            {
                "employee_name": emp["_id"],
                "designation": get_designation(emp["_id"]),
                "total_hours": emp["total_hours"]
            }
            for emp in pm_data
        ]

        # Calculate total hours spent on the project
        total_project_hours = sum(emp["total_hours"] for emp in employees_list)

        #return {
        #    "employees": employees_list,
        #    "total_project_hours": total_project_hours
        #}
        employees_list,total_project_hours

    except Exception as e:
        return {"error": str(e)}