'''
Manager: hosts the status/variable information from Nodes, handles POST requests from Nodes
and Controller to collect and distribute information
'''

from flask import Flask, request
import utilities
import os  # to generate the ssl keys
import threading
import datetime

app = Flask(__name__)


@app.route("/")
def index():
    return "Successfully running Syncopate! This is the Manager."

@app.route("/dev")
def dev_test():
    return str(utilities.node_information)

# receives a command from a controller
@app.route("/controller", methods=["POST"])
def controller():
    controller_access_token = request.form["access-token"]
    action = request.form["action"]
    response = {}

    valid_actions = ["start", "stop", "restart", "status", "add", "remove"]
    if action not in valid_actions:
        response["request-status"] = "failure"
        response["request-information"] = "invalid action"
        return str(response)

    elif action == "start":
        projects = dict(request.form["projects"])
        utilities.startProjects(projects) 
        return str("success")

    elif action == "stop":
        projects = dict(request.form["projects"])
        utilities.stopProjects(projects)
        return str("success")

    elif action == "restart":
        projects = dict(request.form["projects"])
        utilities.stopProjects(projects)
        utilities.startProjects(projects)
        return str("success")

    elif action == "status":
        projects = dict(request.form["projects"])
        response = utilities.getStatuses(projects)
        return response

    elif action == "add":
        projects = dict(request.form["projects"])
        utilities.addProjects(projects)
        return str("success")

    elif action == "remove":
        projects = dict(request.form["projects"])
        utilities.removeProjects(projects)
        return str("success")


# receives update information from a Node
@app.route("/node-update", methods=["POST"])
def node_update():
    node_access_token = request.form["access-token"]
    node_name = request.form["name"]
    project_name = request.form["project-name"]
    project_url = request.form["project-url"]
    project_status = request.form["status"]
    project_disk_usage = request.form["disk-usage"]
    project_ram_usage = request.form["ram-usage"]
    project_persistent_variables = request.form["persistent-variables"]

    update_info = ""
    if node_name not in utilities.node_information.keys():
        update_info = "error: invalid node name"
    elif node_access_token != utilities.node_information[node_name]["access-token"]:
        update_info = "error: invalid access token"
    elif project_name not in utilities.node_information[node_name]["projects"].keys():
        update_info = "error: project not assigned to this node"
    elif project_url not in utilities.node_information[node_name]["projects"][project_name]["url"]:
        update_info = "error: project url incorrect"

    update_result = "success"
    if update_info != "":
        update_result = "failure"
    
    utilities.node_information[node_name]["projects"][project_name]["status"] = project_status
    utilities.node_information[node_name]["projects"][project_name]["disk-usage"] = project_disk_usage
    utilities.node_information[node_name]["projects"][project_name]["ram-usage"] = project_ram_usage
    utilities.node_information[node_name]["projects"][project_name]["persistent-variables"] = project_persistent_variables
    utilities.node_information[node_name]["last-contact"] = datetime.datetime.now().timestamp()

    response = {
        "update-result": update_result,
        "update-info": update_info
    }

    return str(response)


# request node information for a Node
@app.route("/node-status", methods=["POST"])
def node_status():
    node_access_token = request.form["access-token"]
    node_name = request.form["name"]

    if node_access_token != utilities.node_information[node_name]["access-token"]:
        return "Invalid access token"

    projects = utilities.node_information[node_name]["projects"]

    # remove information unnecesary to the node
    for project_name in projects:
        del projects[project_name]["status"]
        del projects[project_name]["disk-usage"]
        del projects[project_name]["ram-usage"]

    response = {
        "name": node_name,
        "projects": projects
    }

    return str(response)

@app.route("/node-initialize", methods=["POST"])
def node_initialize():
    # node information from the POST request
    node_preferred_name = request.form["preferred-name"]
    syncopate_password = request.form["syncopate-password"]
    storage_available = request.form["storage"]
    ram_available = request.form["ram"]
    
    response = {}  # POST response from the Manager
    
    # check password
    if syncopate_password != utilities.settings["server-password"]:
        response["initialization-result"] = "failure"
        response["failure-reasoning"] = "incorrect syncopate password"
        return str(response)

    # determine the node name
    current_node_names = utilities.node_information.keys()
    node_name = node_preferred_name
    if node_name in current_node_names:
        node_name = utilities.generateNodeName(current_node_names)
    # receiving "-1" from the generateNodeName() indicates failure!
    if node_name == "-1":
        response["initialization-result"] = "failure"
        response["failure-reasoning"] = "unable to generate a node name"
        return str(response)

    # everything checks out!
    # generate the node
    utilities.node_information[node_name] = utilities.generateBaseNode()
    utilities.node_information[node_name]["name"] = node_name
    utilities.node_information[node_name]["access-token"] = utilities.generateAccessToken()
    utilities.node_information[node_name]["storage"] = storage_available
    utilities.node_information[node_name]["ram"] = ram_available
    
    # generate the response
    response["initialization-result"] = "success"
    response["name"] = node_name
    response["access-token"] = utilities.node_information[node_name]["access-token"]

    return str(response)

if __name__ == "__main__":
    utilities.getSettings()
    utilities.getProjects()
    manager_thread = threading.Thread(target=utilities.status_check, args=[])
    manager_thread.start()
    app.run()
