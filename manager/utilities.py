'''
Manager Utilities: contains several functions to support the server
'''
import secrets, string  # for creating the access token
import random  # for generating node name
import time
import datetime

node_information = {}
project_information = {}
active_projects = {}
settings = {}

def getSettings():
    with open("manager.settings", "r") as settings_file:
        lines = settings_file.readlines()
        settings["server-password"] = lines[0]
    return

# periodically checks if the nodes are alive, if any are dead start them
def status_check():
    while True:
        for project in active_projects.keys():
            # check the timestamp, compare to the timeout
            last_checkin = active_projects[project]["last-checkin"]
            timeout = active_projects[project]["timeout"]
            if datetime.datetime.now().timestamp() > int(last_checkin) + int(timeout):
                active_projects[project]["status"] = "dead"
                stopProjects([project])
                startProjects([project])
                continue

            current_ram = active_projects[project]["ram"]
            current_disk = active_projects[project]["disk"]

            project_information[project]["status"] = "alive"
            project_information[project]["ram"] = current_ram
            project_information[project]["disk"] = current_disk

        time.sleep(3)
    return

def stopProjects(projects):
    for project_name in projects:
        for node in node_information.keys():
            if project_name in node["projects"]:
                projects.remove(project_name)
    return


# figures out an ideal Node to start the project, adds to node information
def startProjects(projects):
    for project_name in projects:
        if project_name not in project_information.keys():
            continue

        ideal_node = node_information.keys()[0]

        for node_name in node_information.keys():
            ram = int(node_information[node_name]["ram"])
            disk = int(node_information[node_name]["disk"])
            for project in node_information[node_name]["projects"].keys():
                ram -= node_information[node_name]["projects"][project]["ram"]
                disk -= node_information[node_name]["projects"][project]["disk"]
            if project_information[project_name]["ram"] < ram and project_information[project_name]["disk"] < disk:
                if ram > node_information[ideal_node]["ram"] and disk > node_information[ideal_node]["disk"]:
                    ideal_node = node_name

        node_information[ideal_node]["projects"][project_name] = project_information[project]
        
def getStatuses(projects):
    response = {}
    for project_name in projects:
        response[project_name] = "unknown"
        for node in node_information.keys():
            if project_name in node["projects"]:
                response[project_name] = node["projects"][project_name]["status"]
    return response

def addProjects(projects):
    for project_name in projects.keys():
        project_information[project_name] = projects[project_name] 
    return

def removeProjects(projects):
    for project_name in projects:
        del project_information[project_name]
    return

# generates a random alphanumeric string of a specified length
def generateAlphaNumericString(length):
    token = ""  # base access token
    for i in range(0, length):
        token += secrets.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)  # adds "length" items to the token   
    return token


# generates an access token, defaults to 64 characters long
def generateAccessToken(length=64):
    return generateAlphaNumericString(length)


# generates a random Node name
def generateNodeName(current_names):
    node_name = ""

    with open("node_names.txt", "r") as node_names_file:  # node_names.txt contains a list of possible names
        names = []
        for name in node_names_file.readlines():
            names.append(name[:-1])
        
        # try choosing random node names, if it doesn't work after len(names) tries...

        for i in range(0, len(names)):
            potential_node_name = random.choice(names)
            if potential_node_name not in current_names:
                node_name = potential_node_name
                break
        if node_name != "":
            return node_name

        # go through each of the names file sequentially, if all the names there are used...
        for name in names:
            potential_node_name = name
            if potential_node_name not in current_names:
                node_name = potential_node_name
                break
        if node_name != "":
            return node_name
        
        # generate a 6 digit random alphanumeric name until one works (this limits us to 56.8 billion nodes, which should be fine)
        # try a max of 1,000,000 times
        for i in range(0, 1000000):
            potential_node_name = generateAlphaNumericString(6)
            if potential_node_name not in current_names:
                node_name = potential_node_name
                break
    
    # if all our efforts to generate a unique name fail...
    if node_name in current_names:
        return "-1"
    return node_name



# generate the base empty node structure
def generateBaseNode():
    node = {}
    node["name"] = ""  # redundant, as the dictionary name is the node name, this is a check
    node["access-token"] = ""    
    node["projects"] = {}
    node["storage"] = ""
    node["ram"] = ""
    return node

