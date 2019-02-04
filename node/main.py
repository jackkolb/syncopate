'''
Node: periodically requests current assignments from the manager, downloads projects etc as required
'''


from urllib.parse import urlencode
from urllib.request import Request, urlopen
import time
import subprocess
import psutil
import ast
import os

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
        global projects
        print(projects)
        # see if all the projects have been started, if not start projects that haven't been started yet
        for project_name in projects.keys():
            if not checkProjectHasStarted(project_name):
                startProject(project_name)

            updateManager(project_name)  # update the Manager on each project


    return


def checkProjectHasStarted(project_name):
    if "process" not in projects[project_name].keys() or projects[project_name]["process"] == "":
        return False
    return True


def checkProjectIsAlive(project_name):
    if projects[project_name]["process"].poll() == None:
        return True
    return False


# returns disk usage of a project, in KB
def getProjectDiskUsage(project_name):
    total_size = 0
    seen = set()

    for dirpath, dirnames, filenames in os.walk("./" + project_name):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                stat = os.stat(fp)
            except OSError:
                continue
            if stat.st_ino in seen:
                continue
            seen.add(stat.st_ino)
            total_size += stat.st_size
    return total_size / 1024


def getProjectRamUsage(project_name):
    return psutil.Process(projects[project_name]["process"].pid).memory_info


def getProjectVariables(project_name):
    with open("./" + project_name + "/project.variables", "r") as variables_file:
        data = ast.literal_eval(variables_file.readline())
    return data


def startProject(project_name):
    print("Cloning git URL for project " + project_name)
    git_clone = subprocess.Popen(["git", "clone", projects[project_name]["project-url"], project_name])
    git_clone.wait()
    print("Starting project" + project_name)
    projects[project_name]["process"] = subprocess.Popen(["./" + project_name + "/run.sh"])


# updates the manager with project information
def updateManager(project_name):
    project = projects[project_name]
    project_url = project["project-url"]
    project_status = "Alive" if checkProjectIsAlive(project_name) else "Dead"
    project_disk_usage = getProjectDiskUsage(project_name)
    project_variables = getProjectVariables(project_name)
    data = {
        "access-token": access_token,
        "name": node_name,
        "project-name": project_name,
        "project-url": project_url,  # for confirmation
        "status": project_status,
        "disk-usage": project_disk_usage,
        "ram-usage": getProjectRamUsage,
        "persistent-variables": project_variables
    }

    response = postRequest("node-update", data)
    print(response)
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
    