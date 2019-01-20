# Syncopate

THIS PROJECT IS VERY MUCH A WORK IN PROGRESS!! DO READ THE README TO SEE THE CURRENT STATUS!

Syncopate manages and syncs a network of devices, to provide an overview of a collection of Raspberry Pis (or other such devices) and manage a number of persistent-time projects in an automated manner.

## Intended Project Scope
Nodes: the rack of Raspberry Pis on your desk
Manager: the central server that names nodes, assigns tasks, and publishes status information (hosted on AWS/GCP/elsewhere)
Controller: the cute GUI you run on your laptop to manage the Nodes, communicates with the Manager

Overall, Nodes are given a list of GitHub projects to sync with and run
- Nodes read from Manager their project assignments, and send status information back to Manager
- Controller can see the status of the various devices and projects
- Controller can add/remove projects (security regarding this will be interesting...)
- Manager balances projects to devices automatically as devices are added/disconnected

## Completed Features
None yet!
