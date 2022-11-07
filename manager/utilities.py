'''
Manager Utilities: contains several functions to support the server
'''
import secrets, string  # for creating the access token
import random  # for generating node name
import time
import datetime
import ast

node_information = {}
project_information = {}  # long term storage project information (persists beyond this process and saved to disk)
active_projects = {}  # copy of project_information, however also has the fields "last-contact" and "status"
settings = {}
standby_projects = {}

# periodically checks if the nodes are alive, if any are dead start them
def status_check():
    global project_information, active_projects
    while True:
        #print("checking statuses")
        for project in active_projects.keys():
            # check the timestamp, compare to the timeout
            last_contact = active_projects[project]["last-contact"]
            timeout = active_projects[project]["timeout"]
            if last_contact == "0":
                active_projects[project]["status"] = "unborn"
                stopProjects([project])
                startProjects([project])
                continue

            elif datetime.datetime.now().timestamp() > int(last_contact) + int(timeout):
                print(project + " is dead")
                active_projects[project]["status"] = "dead"
                stopProjects([project])
                startProjects([project])
                continue

            current_ram = active_projects[project]["project-ram"]
            current_disk = active_projects[project]["project-storage"]
            active_projects[project]["status"] = "alive"
            project_information[project]["ram-estimate"] = current_ram
            project_information[project]["storage-estimate"] = current_disk
        with open("manager.projects", "w") as projects_file:
            projects_file.write(str(project_information))
        time.sleep(3)
    return


def getSettings():
    with open("manager.settings", "r") as settings_file:
        lines = settings_file.readlines()
        settings["server-password"] = lines[0]
    return


def getProjects():
    with open("manager.projects", "r") as projects_file:
        global project_information
        global active_projects
        project_information = ast.literal_eval(projects_file.readline())
        active_projects = project_information
        for project in active_projects.keys():
            active_projects[project]["status"] = "dead"
            active_projects[project]["last-contact"] = "0"
            active_projects[project]["timeout"] = "30"

            if "ram-estimate" not in project_information.keys():
                project_information[project]["ram-estimate"] = "1"
            if "storage-estimate" not in project_information.keys():
                project_information[project]["storage-estimate"] = "1"
    return


def stopProjects(projects):
    for project_name in projects:
        for node in node_information.keys():
            if project_name in node_information[node]["projects"]:
                projects.remove(project_name)
    return


# figures out an ideal Node to start the project, adds to node information
def startProjects(projects):
    global node_information

    # if there are no registered nodes, can't start projects
    if len(node_information.keys()) == 0:
        return
        
    for project_name in projects:
        if project_name not in project_information.keys():
            print("[info] startProjects project name not in project informations")
            continue

        ideal_node = ""
        print(":::::::::::" + project_name)

        for node_name in node_information.keys():
            ram = int(node_information[node_name]["ram"])
            disk = int(node_information[node_name]["storage"])
            for project in node_information[node_name]["projects"].keys():
                ram -= int(node_information[node_name]["projects"][project]["project-ram"])
                disk -= int(node_information[node_name]["projects"][project]["project-storage"])
            if int(project_information[project_name]["ram-estimate"]) < ram and int(project_information[project_name]["storage-estimate"]) < disk:
                if ideal_node == "":
                    ideal_node = node_name
                elif ram > int(node_information[ideal_node]["ram"]) and disk > int(node_information[ideal_node]["storage"]):
                    ideal_node = node_name
        print(node_information)
        node_information[ideal_node]["projects"][project_name] = project_information[project_name]
        

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

