import datetime
import requests

# url = 'http://localhost:8080'
url = 'https://nacelle-microframework.appspot.com'
suffix = '/mailer/send_scheduled'


for x in range(10):

    time = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)

    data = dict(
            time_scheduled=time.isoformat(),
            sender='paddyc23@googlemail.com',
            to='patrick@rehabstudio.com',
            subject='Just Testing',
            body_plain='Test',
            body_html='<h1>Test</h1>',
        )

    r = requests.post(url + suffix, data=data)
    print r.json
