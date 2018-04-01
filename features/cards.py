import urllib
import requests
import json
import datetime
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import logging

logger = logging.getLogger('discord')


def get_card_url(command):
    logger.info("Getting a card URL for " + str(command))
    card_name = ''

    for string in command:
        if card_name != '':
            card_name += ' '
        card_name += string.lower()

    valid_name, url_or_potentials = validate_card_name(card_name)
    if valid_name:
        logger.info("It's a valid card, posting the URL now")
        return url_or_potentials
    else:
        if isinstance(url_or_potentials, list):
            message = ""
            for card, _ in url_or_potentials:
                if message != "":
                    message += ", "
                message += prettify_name(card)
            logger.info("It's not a valid card, posting alternatives now")
            return "I'm sorry, honourable samurai-san, but this card is not known. \n" + \
                   "Perhaps you meant one of these three? \n" + message
        else:
            return "I'm guessing you meant this card: \n" + \
                   url_or_potentials


def validate_card_name(card_name):
    """Returns the card name or potential alternatives."""

    logger.info("Checking whether the card is an existing card")
    with open('card_db.json', 'r') as json_data:
        try:
            db_records = json.load(json_data)
        except json.decoder.JSONDecodeError:
            db_records = {}

    if db_records == {} or (datetime.datetime.strptime(db_records['last_updated'], "%Y-%m-%dT%H:%M:%S.%f") - datetime.datetime.today()).days < 0:
        logger.info("Updating Card DB")
        r = requests.get("https://api.fiveringsdb.com/cards")
        request_data = r.json()

        db_records['last_updated'] = datetime.datetime.today().isoformat()
        card_names = {}
        for card in request_data['records']:
            image_url = find_image_url(card['pack_cards'])
            card_names[card['name_canonical']] = image_url
        db_records['cards'] = card_names
        with open('card_db.json', 'w') as outfile:
            json.dump(db_records, outfile)
            logger.info('Saved new card_db to file')

    if card_name in db_records['cards']:
        logger.info("Found card in DB")
        return True, db_records['cards'][card_name]

    logger.info("Presenting alternatives")
    potentials = process.extract(card_name, set(db_records['cards']), limit=3, scorer=fuzz.ratio)
    if fuzz.partial_ratio(card_name, potentials[0]) >= 75:
        logger.info("Found a good match in DB")
        logger.info("Matched " + str(card_name) + " to " + str(potentials[0][0]) + " with similarity of " + str(potentials[0][1]))
        return False, db_records['cards'][potentials[0][0]]

    return False, potentials


def find_image_url(card_packs):
    for pack in card_packs:
        if "image_url" in pack:
            return pack['image_url']
    return "No image available"


def prettify_name(cardname):
    cardname = cardname.split(" ")
    pretty = ""
    for word in cardname:
        pretty += word.capitalize() + " "

    return pretty
