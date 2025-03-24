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