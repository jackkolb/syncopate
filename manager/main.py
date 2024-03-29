'''
Manager: hosts the status/variable information from Nodes, handles POST requests from Nodes
and Controller to collect and distribute information
'''

from flask import Flask, request, jsonify, render_template
import utilities
import os  # to generate the ssl keys
import threading
import datetime
import logging
import json

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dev")
def dev_test():
    return jsonify(utilities.node_information)

# receives a command from a controller
@app.route("/controller", methods=["POST"])
def controller():
    data = json.loads(request.get_data().decode())
    controller_access_token = data["access-token"]
    action = data["action"]
    response = {"code": 0}

    valid_actions = ["start", "stop", "restart", "project-status", "node-status", "add", "remove"]
    if action not in valid_actions:
        response["request-status"] = "failure"
        response["request-information"] = "invalid action"

    elif action == "start":
        projects = dict(request.form["projects"])
        utilities.startProjects(projects) 

    elif action == "stop":
        projects = dict(request.form["projects"])
        utilities.stopProjects(projects)

    elif action == "restart":
        projects = dict(request.form["projects"])
        utilities.stopProjects(projects)
        utilities.startProjects(projects)

    elif action == "project-status":
        projects = data["projects"] if "projects" in data else []
        response = utilities.getProjectStatuses(projects)
    
    elif action == "node-status":
        projects = data["nodes"] if "nodes" in data else []
        response = utilities.getNodeStatuses(projects)

    elif action == "add":
        projects = dict(request.form["projects"])
        utilities.addProjects(projects)

    elif action == "remove":
        projects = dict(request.form["projects"])
        utilities.removeProjects(projects)
    
    return jsonify(response)


# handler to receive project update information from a Node
@app.route("/node-update", methods=["POST"])
def node_update():
    node_access_token = request.form["access-token"]
    node_name = request.form["name"]
    project_name = request.form["project-name"]
    project_url = request.form["project-url"]
    project_status = request.form["status"]
    project_disk_usage = request.form["project-storage"]
    project_ram_usage = request.form["project-ram"]
    project_persistent_variables = request.form["persistent-variables"]

    response = {}

    update_info = ""
    if node_name not in utilities.node_information.keys():
        response["code"] = 100
        response["failure-reasoning"] = "invalid node name"
        return jsonify(response)
    elif node_access_token != utilities.node_information[node_name]["access-token"]:
        update_info = "error: invalid access token"
        response["code"] = 101
        response["failure-reasoning"] = "invalid access token"
        return jsonify(response)
    elif project_name not in utilities.node_information[node_name]["projects"].keys():
        response["code"] = 102
        response["failure-reasoning"] = "project not assigned to this node"
        return jsonify(response)
    elif project_url not in utilities.node_information[node_name]["projects"][project_name]["project-url"]:
        response["code"] = 103
        response["failure-reasoning"] = "incorrect project url"
        return jsonify(response)

    update_result = "success"
    if update_info != "":
        update_result = "failure"
        
    utilities.node_information[node_name]["projects"][project_name]["status"] = project_status
    utilities.node_information[node_name]["projects"][project_name]["project-storage"] = project_disk_usage
    utilities.node_information[node_name]["projects"][project_name]["project-ram"] = project_ram_usage
    utilities.node_information[node_name]["projects"][project_name]["persistent-variables"] = project_persistent_variables
    
    timestamp = datetime.datetime.now().timestamp()
    utilities.active_projects[project_name]["last-contact"] = timestamp
    utilities.node_information[node_name]["last-contact"] = timestamp

    response = {
        "code": 0,
        "update-result": update_result,
        "update-info": update_info
    }

    print("Received update information from node: " + node_name)

    return jsonify(response)


# handlers for nodes to request their own project information
@app.route("/node-status", methods=["POST"])
def node_status():
    node_access_token = request.form["access-token"]
    node_name = request.form["name"]

    # if the node name does not exist, return that it's invalid (node will reinitialize)
    if node_name not in utilities.node_information:
        response = {
            "code": 100,
            "failure-reasoning": "node name does not exist"
        }
        return jsonify(response)

    if node_access_token != utilities.node_information[node_name]["access-token"]:
        response = {
            "code": 11,
            "failure-reasoning": "incorrect access token"
        }
        return jsonify(response)

    projects = utilities.node_information[node_name]["projects"]

    response = {
        "code": 0,
        "name": node_name,
        "projects": projects
    }

    print("Gave status information to node: " + node_name)
    utilities.node_information[node_name]["last-contact"] = datetime.datetime.now().timestamp()

    return jsonify(response)


# handler for nodes to initialize themselves
@app.route("/node-initialize", methods=["POST"])
def node_initialize():
    # node information from the POST request
    node_preferred_name = request.form["preferred-name"]
    syncopate_password = request.form["syncopate-password"]
    storage_available = request.form["storage"]
    ram_available = request.form["ram"]
    
    response = {"code": 1}  # POST response from the Manager
    
    # check password
    if syncopate_password != utilities.settings["server-password"]:
        response["initialization-result"] = "failure"
        response["failure-reasoning"] = "incorrect syncopate password"
        return jsonify(response)

    # determine the node name
    current_node_names = utilities.node_information.keys()
    node_name = node_preferred_name
    if node_name in current_node_names:
        node_name = utilities.generateNodeName(current_node_names)
    # receiving "-1" from the generateNodeName() indicates failure!
    if node_name == "-1":
        response["initialization-result"] = "failure"
        response["failure-reasoning"] = "unable to generate a node name"
        return jsonify(response)

    # everything checks out!
    # generate the node
    utilities.node_information[node_name] = utilities.generateBaseNode()
    utilities.node_information[node_name]["name"] = node_name
    utilities.node_information[node_name]["access-token"] = utilities.generateAccessToken()
    utilities.node_information[node_name]["storage"] = storage_available
    utilities.node_information[node_name]["ram"] = ram_available
    
    # generate the response
    response = {
        "code": 0,
        "initialization-result": "success",
        "name": node_name,
        "access-token": utilities.node_information[node_name]["access-token"]
    }
    print("Registered new node: " + node_name, response)
    return jsonify(response)

if __name__ == "__main__":
    utilities.getSettings()
    utilities.getProjects()
    manager_thread = threading.Thread(target=utilities.status_check, args=[])
    manager_thread.start()
    #app.logger.disabled = True
    #log = logging.getLogger('werkzeug')
    #log.disabled = True
    app.run()
