import random
import grequests
import json

# random_nums = range(5000000)
requests_at_a_time = 25
total_requests = 2500

# url = 'http://localhost:8080'
url = 'https://nacelle-microframework.appspot.com'
suffix = '/demo/count'


def request_generator(num_requests=100):
    for x in range(num_requests):
        data = {'someint': random.randint(1, 100)}
        yield grequests.post(url + suffix, data=json.dumps(data), config={"max_retries": 10})

print "Making %d API calls" % total_requests
count = 1
requests = grequests.imap(request_generator(total_requests), size=requests_at_a_time)
for x in requests:
    print str(count) + ' ' + str(x)
    count += 1
