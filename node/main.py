'''
Node: periodically requests current assignments from the manager, downloads projects etc as required
'''


from urllib.parse import urlencode
from urllib.request import Request, urlopen
import time
import subprocess
import psutil
import ast

projects = {}
settings = {}

node_name = ""
access_token = ""

def main():
    getSettings()
    initialize()
    while True:
        time.sleep(5)
        getNodeInformation()
        print(projects)
    return


# updates the manager with project information
def updateManager():
    
    return


# request node information
def getNodeInformation():
    data = {
        "name": node_name,
        "access-token": access_token
    }
    response = postRequest("node-status", data)
    global projects
    projects = ast.literal_eval(response)
    return

# sends initialization request to the manager
def initialize():
    data = {}
    data["preferred-name"] = settings["preferred-name"]
    data["syncopate-password"] = settings["syncopate-password"]
    data["storage"] = getAvailableStorage()
    data["ram"] = getAvailableRam()
    manager_response = postRequest("node-initialize", data)
    manager_response = ast.literal_eval(manager_response)
    if manager_response["initialization-result"] == "success":
        global node_name, access_token
        node_name = manager_response["name"]
        access_token = manager_response["access-token"]
        print("Successfully registered as a node")
        print("Name: " + node_name)
        print("Token: " + access_token)
    else:
        print("Failed to register Node: " + manager_response["failure-reasoning"])
    return




def postRequest(route, data):
    url = settings["manager-url"] + "/" + route
    post_request = Request(url, urlencode(data).encode())
    response = urlopen(post_request).read().decode()
    return response


def getSettings():
    with open("node.settings", "r") as setup_file:
        lines = setup_file.readlines()
        settings["manager-url"] = lines[0][:-1]
        settings["preferred-name"] = lines[1][:-1]
        settings["syncopate-password"] = lines[2]
    return


def getAvailableRam():
    df = subprocess.Popen(["free", "-m"], stdout=subprocess.PIPE)
    output = str(df.communicate()[0]).split("\\n")[1].split(" ")
    output = [x for x in output if x != ""][6]
    return output


def getAvailableStorage():
    df = subprocess.Popen(["df", "/"], stdout=subprocess.PIPE)
    output = str(df.communicate()[0]).split("\\n")[1].split(" ")
    output = [x for x in output if x != ""][3]
    output = int(int(output)/1048576*1000)/1000
    return output 


if __name__ == "__main__":
    main()
    