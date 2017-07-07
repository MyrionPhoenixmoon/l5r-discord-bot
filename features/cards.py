import urllib
import requests
import logging


logger = logging.getLogger('discord')


def get_card_url(command):

    logger.info("Getting a card URL for " + str(command))
    card_name = ''

    for string in command:
        string = urllib.parse.unquote(string)
        string = string.replace("'", "-")
        if card_name != '':
            card_name += '-'
        card_name += string.lower()

    if validate_card(card_name):
        return "https://fiveringsdb.com/bundles/card_images/" + card_name + ".png"
    else:
        return "I'm sorry, honourable samurai-san, but this card is not known."


def validate_card(card_name):

    r = requests.get("https://fiveringsdb.com/api/v1/cards/" + card_name)
    if r.status_code != "200":
        return False

    return True
