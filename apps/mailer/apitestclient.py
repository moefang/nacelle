import grequests
import json

requests_at_a_time = 5
total_requests = 20
url = 'http://localhost:8080/api/mailer'
#url = 'https://nacelle-microframework.appspot.com/api/mailer'


def request_generator(num_requests=100):
    for x in range(num_requests):
        data = {
            'sender': 'paddyc23@googlemail.com',
            'to': ['paddyc23@gmail.com'],
            'subject': 'testing',
            'body': 'sdfsdfsdfsdfsdfsdfsdfsdfsdf',
            'time_scheduled': '2012-10-28T05:45:00',
        }
        cookies = {'dev_appserver_login': "test@example.com:True:185804764220139124118"}
        yield grequests.post(url=url, data=json.dumps(data), cookies=cookies)

print "Making %d API calls" % total_requests
count = 1
requests = grequests.imap(request_generator(total_requests), size=requests_at_a_time)
for x in requests:
    print str(count).zfill(7) + ': ' + str(x.text)
    count += 1
