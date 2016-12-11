from bs4 import BeautifulSoup
import requests
import json
from collections import defaultdict
from configobj import ConfigObj
from twilio.rest import TwilioRestClient
import sys

part_num = sys.argv[1]
limit_count = sys.argv[2]

def send_twilio_message(text_message):
    config = ConfigObj('config.ini')

    TWILIO_SID = config['sid']
    TWILIO_TOKEN = config['token']
    TWILIO_NUMBER = config['number']

    client = TwilioRestClient(TWILIO_SID, TWILIO_TOKEN)

    message = client.messages.create(body=text_message,to="+1" + '872-225-6140', from_= TWILIO_NUMBER)

def clean_up(s):
    s = str(s)
    if 'k' in s:
        return int(float(s[:-1]) * 1000)
    else:
        return int(s)
try:
    with open('repo_contributor_data_json.txt', 'r') as f:
        contributors = json.load(f)
        concrete_contributors = defaultdict(list)
        data = [(key,value) for key, value in contributors.iteritems()]
        data.sort(key = lambda a : a[0])
        for key, values in data[:int(limit_count)]:
            for value in values['contributors'] if len(values['contributors']) < 10 else values['contributors'][:10]:
                print value
                print value['login']
                try:
                    html = requests.get('https://github.com/' + value['login'] + '/').content
                    soup = BeautifulSoup(html)
                    data = soup.find_all('span', {'class' : 'counter'}, text=True)
                    repositories = data[0].get_text().strip()
                    stars = data[1].get_text().strip()
                    followers = data[2].get_text().strip()
                    following = data[3].get_text().strip()
                    print repositories, stars, followers, following
                except IndexError:
                    print "^^^^^^^^error above name"
                    continue
                concrete_contributors[key].append({
                        'login': value['login'],
                        'id': value['id'],
                        'followers': clean_up(followers),
                        'following':clean_up(following),
                        'starred':clean_up(stars),
                        'repos':clean_up(repositories)
                    })
        with open('repo_concrete_contributors_json_' + part_num + '.txt', 'w') as ff:
            ff.write(json.dumps(concrete_contributors, sort_keys=True, indent=4, separators=(',', ': ')))
            send_twilio_message('completed part ' + part_num)
except:
    send_twilio_message('Fucking ERROR')