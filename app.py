from flask import Flask, request, jsonify
from pymongo import MongoClient
from Emp_timesheet import add_PM_data, add_AM_data, employee_login,performance_matrices, get_latest_employee_am_data
from Emp_info import add_emp_info
from flask_cors import CORS
import logging
from admin import add_new_user,delete_emp,get_emp_data,show_user, get_timesheet_between_dates, get_am_timesheet_between_dates,get_pm_timesheet_between_dates,get_performance_between_dates, user_details
from Project import retrieve_project,add_project, get_project_list, get_project_hours_pm, get_project_detail, delete_project
#from pyngrok import ngrok
import os

application = Flask(__name__)

CORS(application) 
#CORS(application, resources={r"/": {"origins": ""}}) # Enable CORS for frontend-backend communication
#
## Start ngrok tunnel
#port = 8000  # Set the same port as Flask
#public_url = ngrok.connect(port).public_url
#print(f"Ngrok Tunnel URL: {public_url}")

@application.route("/")
def home():
    return jsonify({"message": "Backend is running successfully!"})

@application.route("/api/routes", methods=["GET"])
def get_routes():
    return jsonify([str(rule) for rule in application.url_map.iter_rules()])

logging.basicConfig(level=logging.DEBUG)

#@application.errorhandler(Exception)  # Capture all unhandled errors
#def handle_exception(e):
#    application.logger.error(f"Error: {e}", exc_info=True)
#    return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@application.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("email")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user_data = employee_login(username, password)  # Check credentials

    if user_data:
        if username =="admin":
            return jsonify({"user": user_data, "message": "Admin login successful"}), 200
        else:
            return jsonify({"user": user_data, "message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401



@application.route("/api/AM", methods=["POST"])
def add_AM_timesheet():
    data = request.json
    add_AM_data(data)
    return jsonify({"message": "Timesheet added successfully"})

@application.route("/api/PM", methods=["POST"])
def add_PM_timesheet():
    data = request.json
    #print(data)
    add_PM_data(data)
    return jsonify({"message": "Timesheet added successfully"})

@application.route("/api/users", methods=["POST"])
def new_users():
    data = request.json
    add_new_user(data)
    return jsonify({"message": "Timesheet added successfully"})

@application.route("/api/users/email/<string:email>", methods=["DELETE"])
def delete_user(email):
    
    delete_emp(email)
    return jsonify({"message": "Employee deleted successfully"})

@application.route("/api/matrices", methods=["POST"])
def matrices():
    data = request.json
    email = data.get("email")
    date = data.get("date")
    ratings = data.get("ratings")
    performance_matrices(email, date, ratings)
    return jsonify({"message": "Performance matrices updated successfully"})

@application.route("/api/add_employee", methods=["POST"])  # Fixed: Added missing route
def add_employee():
    emp_name = request.json
    add_emp_info(emp_name)
    return jsonify({"message": "Employee added successfully"})

# @application.route("/api/timesheet/admin/<string:username>/<string:date>", methods=["GET"])
# def get_timesheet(username, date):
#     data = get_emp_data(username,date)
#     return jsonify({"message": "Employee data fetched successfully", "data": data})

@application.route("/api/timesheet/admin/<string:username>/<string:startDate>/<string:endDate>", methods=["GET"])
def get_timesheet(username, startDate,endDate):
    data = get_timesheet_between_dates(username,startDate,endDate)
    return jsonify({"message": "Employee data fetched successfully", "data": data})

# @application.route("/api/timesheet/user/<string:username>/<string:date>", methods=["GET"])
# def get_user_timesheet(username, date):
#     """
#     Fetch timesheet data for a specific user and date.
#     """
#     try:
#         # Convert the date string to the expected format
#         timesheet_entry = get_latest_employee_am_data(username)
#         if timesheet_entry:
#             return jsonify({"success": True, "data": timesheet_entry}), 200
#         else:
#             return jsonify({"success": False, "message": "No timesheet found"}), 404

#     except Exception as e:
#         return jsonify({"success": False, "error": str(e)}), 500

@application.route("/api/timesheet/user/<string:username>/<string:date>", methods=["GET"])
def get_user_timesheet(username, date):
    """
    Fetch timesheet data for a specific user and date.
    """
    try:
        # Convert the date string to the expected format
        timesheet_entry = get_latest_employee_am_data(username)
        if timesheet_entry:
            return jsonify({"success": True, "data": timesheet_entry}), 200
        else:
            return jsonify({"success": False, "message": "No timesheet found"}), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
    
@application.route("/api/timesheet/showUser", methods=["GET"])
def all_user_details():
    data = show_user()
    return jsonify({"message": "Employee list fetched successfully", "data": data})

@application.route('/api/projects', methods=['GET'])
def get_projects():
    projects = retrieve_project()
    return jsonify(projects)

@application.route('/api/projects', methods=['POST'])
def add_new_project():
    """ Add a new project """
    try:
        project = request.json
        add_project(project)
        return jsonify({"message": "Project added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@application.route('/api/projectslist', methods=['GET'])
def get_projectslist():
    try:
        project_names = get_project_list()
        return jsonify({"success": True, "data": project_names})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
@application.route("/api/projects/<string:project_id>/details", methods=["GET"])
def get_project_details(project_id):
    try:
        # Fetch project details
        project,members_list,total_hours = get_project_hours_pm(project_id)
        return jsonify({
            "success": True,
            "project": project,
            "members": members_list,
            "total_hours": total_hours
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
@application.route("/api/timesheet/am/<username>/<start_date>/<end_date>", methods=["GET"])
def get_am_timesheet(username, start_date,end_date):
    data = get_am_timesheet_between_dates(username,start_date,end_date)
    return jsonify({"message": "Success", "data": data})

@application.route("/api/timesheet/pm/<username>/<start_date>/<end_date>", methods=["GET"])
def get_pm_timesheet(username,start_date,end_date):
    data = get_pm_timesheet_between_dates(username,start_date,end_date)
    return jsonify({"message": "Success", "data": data})

@application.route("/api/matrices/<matrixUsername>/<matrixStartDate>/<matrixEndDate>", methods=["GET"])
def get_performance(matrixUsername,matrixStartDate,matrixEndDate):
    data = get_performance_between_dates(matrixUsername,matrixStartDate,matrixEndDate)
    return jsonify({"message": "Success", "data": data})

@application.route("/api/projects/search", methods=["POST"])
def search_project():
    data = request.json
    project = get_project_detail(data["projectName"],data["projectNumber"])
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    return jsonify(project)

@application.route("/api/users/email/<email>", methods=["POST"])
def get_user(email):
    user = user_details(email)
    if not user:
        return jsonify({"error": "User not found"}), 404

@application.route("/api/projects/delete", methods=["POST"])
def delete_project_from_db():
    try:
        data = request.json
        result = delete_project(data["projectNumber"],data["projectName"])
        if result.deleted_count == 0:
                return jsonify({"message": "Project not found."}), 404
    
        return jsonify({"message": "Project removed successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  
    application.run(host="0.0.0.0", port=port)
    #application.run(host="0.0.0.0", port=port)

