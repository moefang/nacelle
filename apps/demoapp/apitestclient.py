import random
import requests
import json

# random_nums = range(5000000)
# requests_at_a_time = 25
# total_requests = 250000

url = 'http://localhost:8080'
# url = 'https://nacelle-microframework.appspot.com'


# def request_generator(num_requests=100):
#     for x in range(num_requests):
#         data = {'r': 'r'}
#         yield grequests.post(url=url, data=json.dumps(data), config={"max_retries": 0})

# print "Making %d API calls" % total_requests
# count = 1
# requests = grequests.imap(request_generator(total_requests), size=requests_at_a_time)
# for x in requests:
#     print count
#     count += 1

count = 0
suffix = '/demo/dynamic_query'

for x in range(random.randint(1, 100)):
    payload = {'someint': random.randint(1, 100)}
    response = requests.post(url + suffix, data=json.dumps(payload))
    print response.text

while True:
    print 'making call'
    response = requests.get(url + suffix).json
    entities = response['page_size']
    if not entities:
        break
    count += entities
    print count
    suffix = response['next_page']
