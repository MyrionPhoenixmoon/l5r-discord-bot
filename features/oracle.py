import requests

def get_card_url(command):
    databody = {'token': 'MONKEYS', 'query': command}
    r = requests.post('http://l5rdb.net/search', data=databody).json()
    return r['url']
    