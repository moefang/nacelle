import random
import grequests
import string
import json

random_nums = range(5000000)
requests_at_a_time = 20
total_requests = 250000
#url = 'http://localhost:8080/api/fixed'
url = 'https://nacelle-microframework.appspot.com/api/fixed'


def request_generator(num_requests=100):
    for x in range(num_requests):
        data = {'randomnum': random.choice(random_nums), 'randomstr': ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(3))}
        yield grequests.post(url=url, data=json.dumps(data))

print "Making %d API calls" % total_requests
count = 1
requests = grequests.imap(request_generator(total_requests), size=requests_at_a_time)
for x in requests:
    print str(count).zfill(7) + ': ' + str(x.text)
    count += 1
