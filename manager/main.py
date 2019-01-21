'''
Manager: hosts the status/variable information from Nodes, handles POST requests from Nodes
and Controller to collect and distribute information
'''

from flask import Flask, request
import utilities
import os  # to generate the ssl keys

app = Flask(__name__)

node_information = {}

@app.route("/")
def index():
    return "Successfully running Syncopate! This is the Manager."

@app.route("/dev")
def dev_test():
    return str(node_information)

@app.route("/node-initialize", methods=["POST"])
def node_initialize():
    # node information from the POST request
    node_preferred_name = request.form["preferred-name"]
    syncopate_password = request.form["syncopate-password"]
    storage_available = request.form["storage"]
    ram_available = request.form["ram"]
    
    response = {}  # POST response from the Manager
    
    # check password
    if syncopate_password != "qwerty":
        response["initialization-result"] = "failure"
        response["failure-reasoning"] = "incorrect syncopate password"
        return response

    # determine the node name
    current_node_names = node_information.keys()
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
    node_information[node_name] = utilities.generateBaseNode()
    node_information[node_name]["name"] = node_name
    node_information[node_name]["access-token"] = utilities.generateAccessToken()
    node_information[node_name]["storage"] = storage_available
    node_information[node_name]["ram"] = ram_available
    
    # generate the response
    response["initialization-result"] = "success"
    response["name"] = node_name
    response["access-token"] = node_information[node_name]["access-token"]

    return str(response)

if __name__ == "__main__":
    app.run()

