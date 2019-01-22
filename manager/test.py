from urllib.parse import urlencode
from urllib.request import Request, urlopen

def testNodeCreate():
     request = {
         "preferred-name": "apple",
         "syncopate-password": "qwerty",
         "storage": "13",
         "ram": ".5"
     }
 
     req = Request("http://127.0.0.1:5000/node-initialize", urlencode(request).encode())
     response = urlopen(req).read().decode()
     print(response)

def testNodeUpdate():
     request = {
         "preferred-name": "apple",
         "syncopate-password": "qwerty",
         "storage": "13",
         "ram": ".5"
     }
 
     req = Request("http://127.0.0.1:5000/node-update", urlencode(request).encode())
     response = urlopen(req).read().decode()
     print(response)




testNodeCreate()
