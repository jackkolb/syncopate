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
import atexit
import signal

settings = {}
projects = {}

node_name = ""
access_token = ""

def exit_handler():
    for project_name in projects.keys():
        print(projects[project_name])
        try:
            os.kill(projects[project_name]["process"].pid, signal.SIGTERM)
        except:
            pass

def main():
    getSettings()
    initialize()
    while True:
        getNodeInformation()
        # see if all the projects have been started, if not start projects that haven't been started yet
        for project_name in projects.keys():
            if not checkProjectHasStarted(project_name):
                startProject(project_name)

            updateManager(project_name)  # update the Manager on each project
        time.sleep(5)
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
def getProjectStorage(project_name):
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
    return int(total_size / 1024)


# memory usage, MB
def getProjectRamUsage(project_name):
    return int(psutil.Process(projects[project_name]["process"].pid).memory_info().rss / 1000)


def getProjectVariables(project_name):
    try:
        with open("./" + project_name + "/project.variables", "r") as variables_file:
            data = ast.literal_eval(variables_file.readline())
    except FileNotFoundError:
        data = {}
    return data


def startProject(project_name):
    global projects
    print("[info] starting project: " + project_name)
    remove_existing = subprocess.Popen(["rm", "-Rf", projects[project_name]["project-url"], "./projects/" + project_name])
    remove_existing.wait()
    DEVNULL = open(os.devnull, 'w')
    git_clone = subprocess.Popen(["git", "clone", projects[project_name]["project-url"], "./projects/" + project_name], stdout=DEVNULL, stderr=subprocess.STDOUT)
    git_clone.wait()
    subprocess.Popen(["chmod", "+x", "./projects/" + project_name + "/run.sh"])
    projects[project_name]["process"] = subprocess.Popen(["sh", "./projects/" + project_name + "/run.sh"])
    print("[info] project started: " + project_name)


# updates the manager with project information
def updateManager(project_name):
    project = projects[project_name]
    project_url = project["project-url"]
    project_status = "Alive" if checkProjectIsAlive(project_name) else "Dead"
    project_storage = getProjectStorage(project_name)
    project_variables = getProjectVariables(project_name)
    data = {
        "access-token": access_token,
        "name": node_name,
        "project-name": project_name,
        "project-url": project_url,  # for confirmation
        "status": project_status,
        "project-storage": project_storage,
        "project-ram": getProjectRamUsage(project_name),
        "persistent-variables": project_variables
    }

    response = postRequest("node-update", data)
    return


# request node information
def getNodeInformation():
    data = {
        "name": node_name,
        "access-token": access_token
    }
    response = postRequest("node-status", data)
    response = ast.literal_eval(response)

    #print("[Node Information] " + str(response))

    if response["name"] != node_name:
        print("[error] /node-status failure: receive incorrect name in Manager response")
        return

    global projects
    response_projects = response["projects"]
    for project_name in projects.keys():
        if "process" in projects[project_name].keys():
            response_projects[project_name]["process"] = projects[project_name]["process"]

    projects = response_projects
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
        print("[info] successfully registered as a node: " + node_name)
    else:
        print("[error] failed to register node: " + manager_response["failure-reasoning"])
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
    output = int(int(output)/1048576)
    return output 


def checkproc(project_name):
    if "process" in projects[project_name].keys():
        return "true"
    return "false"
    


if __name__ == "__main__":
    atexit.register(exit_handler)
    main()
    