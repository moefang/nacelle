import random
import requests
import string
import json

url = 'http://localhost:8080/api'
x = 1
while True:
    resp = requests.post(url=url, data=json.dumps({'randomnum': random.choice(range(10000)), 'randomstr': ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(3))}))
    # resp = requests.post(url=url, data=json.dumps({'randomstr': ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(3))}))
    # resp = requests.delete(url=url)
    print "%d: %s" % (x, resp.text)
    x += 1
