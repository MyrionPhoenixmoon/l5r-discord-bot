from features.cards import validate_card_name
from features.cards import prettify_name
import urllib
import requests

import logging


logger = logging.getLogger('discord')


def get_rulings(command):
    card_name = ''

    for string in command:
        if card_name != '':
            card_name += ' '
        card_name += string.lower()

    valid_name, cards_or_pack = validate_card_name(card_name)
    if valid_name or isinstance(cards_or_pack, tuple):
        if isinstance(cards_or_pack, tuple):
            logger.info("Guessed a single card")
            card_name = cards_or_pack[1]
        card_name = urllib.parse.unquote(card_name)
        card_name = card_name.replace("'", "-")
        card_name = card_name.replace(" ", "-")
        card_name = card_name.replace("!", "")

        logger.info("It's a valid card, fetching rulings now")
        url = "https://api.fiveringsdb.com/cards/" + card_name + "/rulings"
        response = requests.get("https://api.fiveringsdb.com/cards/" + card_name + "/rulings")
        data = {}
        data['entries'] = response.json()["records"]
        data['url'] = url
        data['card_name'] = cards_or_pack[1]

        return (data, None)
    else:
        message = ""
        for card, _ in cards_or_pack:
            if message != "":
                message += ", "
            message += prettify_name(card)
        logger.info("It's not a valid card, posting alternatives now")
        return (None, "I'm sorry, honourable samurai-san, but this card is not known. \n" + \
               "Perhaps you meant one of these three? \n" + message)
