'''
Manager Utilities: contains several functions to support the server
'''
import secrets, string  # for creating the access token
import random  # for generating node name

# for dev tests
from urllib.parse import urlencode
from urllib.request import Request, urlopen

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

