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
