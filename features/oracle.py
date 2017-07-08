import requests

def get_card_url(command):
    card_name = ''
    for string in command:
        if card_name != '':
            card_name += ' '
        card_name += string.lower()

    databody = {'token': 'MONKEYS', 'query': "%s" % card_name}
    r = requests.post('http://l5rdb.net/search', data=databody).json()
    return r['url']
    