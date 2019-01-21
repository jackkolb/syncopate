# Syncopate

THIS PROJECT IS VERY MUCH A WORK IN PROGRESS!! DO READ THE README TO SEE THE CURRENT STATUS!

Syncopate manages the dynamic assignment and execution of persistent-time projects across a number of devices, with minimal configuration required.

## Intended Project Scope
Nodes: the rack of Raspberry Pis on your desk, they register themselves to the central server, get assignments, and run them

Manager: the central server that names nodes, assigns tasks, and publishes status information (hosted on AWS/GCP/your garage/elsewhere)

Controller: a cute GUI you run on your laptop to manage the Nodes, communicates with the Manager

Nodes are given a list of git projects to sync with and run. I will be using/testing this for GitHub, but you should be able to host your own git server too (GitTea, etc)
- Nodes read from Manager their project assignments, and send status information back to Manager
- Controller can see the status of Nodes and projects
- Controller can add/remove projects (security regarding this will be interesting...)
- Manager balances projects to devices automatically as devices are added/disconnected

## Completed Features
None yet!

## Structure

### Node


### Manager
Manager is a python webserver (using Flask) that hosts the status information of the nodes. Statuses are updated via POST requests from Nodes, and retrieved via POST requests from Controller. Nodes are independent in posting their statuses to Manager, hence the project name Syncopation. After a defined timeout Manager will declare a Node dead and reassign its tasks.

When Nodes are activated, they initialize themselves with the Manager via "/node-initialize". The POST request from the Node is in the form:
{
    "preferred-name": PREFERRED_NAME,  # preferred name of the Node, otherwise one will be assigned to it
    "syncopate-password": PASSWORD_TO_THE_MANAGER,  # allows the Node to be embraced by Manager and given an instance key
    "storage": STORAGE_SPACE_AVAILABLE,  # maximum project size that the Node can handle (not a guarantee that the project won't use more)
    "ram": RAM_AVAILABLE  # maximum RAM that the Node can handle (not a guarantee that the project won't use more)
}

... to which the Manager responds:
{
    "initialization-result": NODE_INITIALIZATION_RESULT,  # result of the initialization: success or failure
    
    # if the initialization result is failure:
    "failure-reasoning": FAILURE_CAUSE  # information on why the initialization failed (invalid password, max nodes connected, etc)
    
    # if the initialization result is success:
    "name": NODE_NAME,  # assigned name of the Node
    "access-token": ACCESS_TOKEN  # randomly generated access token for the Node
}

Manager will try to give a Node it's preferred name, and the Node will use the assigned name and access-token for its requests.
The Node name "-1" is reserved to flag an error in the name generation!

Manager receives project status information from Nodes via "/node-update", each project sends its own status. The POST request from the Node is in the form:
{
    "access-token": NODE_SPECIFIC_ACCESS_TOKEN,  # randomly generated upon node assignment
    "name": NAME_OF_THE_NODE,  # determined beforehand, possible names can be configured
    "project-name": NAME_OF_THE_PROJECT,  # the git project name
    "project-url": URL_OF_THE_PROJECT,  # the url of the project (for confirmation)
    "status": STATUS,  # good or bad
    "disk-usage": DISK_USAGE,  # amount of disk space the project is using (for stats for the manager's future project allocation)
    "ram-usage": RAM_USAGE,  # amount of RAM the project is using (for stats for the manager's future project allocation)
    "persistent-variables": {  # variables the server should store in case of node realignment, done as a Dictionary
        "var1": ...,
        "var2": ...,
        "var3": ...
    }
}

... to which Manager responds:
{
    "update-result": NODE_UPDATE_RESULT,  # result of the request: success or failure
    "update-info": OTHER_INFORMATION  # other information of the request: if success: nothing, if failure/invalid: error information
}

Manager stores Node information in a dictionary object, restarting Manager will restart all Nodes

Manager posts information to Controller via "/controller". The POST request from the Controller is in the form:
{
    "access-token": MANAGER_ACCESS_TOKEN,  # randomly generated upon manager start
    "action": ACTION,  # command for the Manager: start, restart, stop, status, add, remove
    
    # action:start requires:
    "projects": ["project1", "project2", ...]  # projects to start, an empty list means all projects
    
    # action:restart requires:
    "projects": ["project1", "project2", ...]  # projects to restart, an empty list means all projects

    # action:stop requires:
    "projects": ["project1", "project2", ...]  # projects to stop, an empty list means all projects

    # action:status requires:
    "projects": ["project1", "project2", ...]  # projects to get statuses on, an empty list means all projects

    # action:add requires:
    "project": {
        "name": PROJECT_NAME,  # name of the project
        "url": PROJECT_URL,  # url of the project
        "initial_variables": {  # initial variables for the project
            "var1": ...,
            "var2": ...,
            "var3": ...
        }
    }

    # action:remove requires:
    "project": {
        "name": PROJECT_NAME,  # name of the project
        "url": PROJECT_URL  # url of the project (for confirmation)
    }
}


### Controller

