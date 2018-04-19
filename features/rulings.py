from features.cards import prettify_name
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import urllib
import requests
import discord
import json

import logging

logger = logging.getLogger('discord')

DESCRIPTION_TEXT = 'Click the links for more information'
TITLE_TEXT = 'Rulings from fiveringsdb.com'


def get_rulings(command):
    card_name = ''

    for string in command:
        if card_name != '':
            card_name += ' '
        card_name += string.lower()

    valid_name, found = find_card_name(card_name)
    if valid_name:
        card_name = found
        data = {'card_name': card_name}
        card_name = urllib.parse.unquote(card_name)
        card_name = card_name.replace("'", "-")
        card_name = card_name.replace(" ", "-")
        card_name = card_name.replace("!", "")

        logger.info("It's a valid card, fetching rulings now")
        url = "https://fiveringsdb.com/card/" + card_name
        logger.info(url)
        response = requests.get("https://api.fiveringsdb.com/cards/" + card_name + "/rulings")

        entries = response.json()["records"]
        data['entries'], split_at = split_rulings(entries)
        data['url'] = url

        if split_at > 0:
            em1 = discord.Embed(title=TITLE_TEXT, description=DESCRIPTION_TEXT,
                                colour=0xDEADBF, url=data['url'])
            for entry in data['entries'][0:split_at]:
                em1.add_field(name=(entry['link'] if entry['link'] is not None else entry['source']), value=entry['text'])
            em2 = discord.Embed(title=TITLE_TEXT, description=DESCRIPTION_TEXT,
                                colour=0xDEADBF, url=data['url'])
            for entry in data['entries'][split_at:]:
                em2.add_field(name=(entry['link'] if entry['link'] is not None else entry['source']), value=entry['text'])
            em1.set_author(name=prettify_name(data['card_name']) + " Part 1")
            em2.set_author(name=prettify_name(data['card_name']) + " Part 2")
            return [em1, em2], None
        else:
            em = discord.Embed(title=TITLE_TEXT, description=DESCRIPTION_TEXT,
                               colour=0xDEADBF, url=data['url'])
            for entry in data['entries']:
                em.add_field(name=(entry['link'] if 'link' in entry else entry['source']), value=entry['text'])
            em.set_author(name=prettify_name(data['card_name']))
            return [em], None
    else:
        message = ""
        for card, _ in found:
            if message != "":
                message += ", "
            message += prettify_name(card)
        logger.info("It's not a valid card, posting alternatives now")
        return (None, "I'm sorry, honourable samurai-san, but this card is not known. \n" + \
                "Perhaps you meant one of these three? \n" + message)


def find_card_name(card_name):
    """Returns the card name or potential alternatives."""

    logger.info("Checking whether the card is an existing card")
    with open('card_db.json', 'r') as json_data:
        try:
            db_records = json.load(json_data)
        except json.decoder.JSONDecodeError:
            db_records = {}

    if card_name in db_records['cards']:
        logger.info("Found card in DB")
        return True, card_name

    logger.info("Presenting alternatives")
    potentials = process.extract(card_name, set(db_records['cards']), limit=3, scorer=fuzz.ratio)
    if fuzz.partial_ratio(card_name, potentials[0]) >= 75:
        logger.info("Found a good match in DB")
        logger.info("Matched " + str(card_name) + " to " + str(potentials[0][0]) + " with similarity of " + str(potentials[0][1]))
        return True, potentials[0][0]

    return False, potentials


def split_rulings(entries):
    cleaned = []
    char_count = 0
    split_embed_at = 0
    count = 1
    for entry in entries:
        entry['text'] = entry['text'] + ("\n[" + entry['source'] + "](" + entry['link'] + ")" if 'link' in entry else '')
        char_count += len(str(count)) + len(entry['text'])
        if len(entry['text']) > 1024:
            text = entry['text']
            first = True
            while len(text) > 1024:
                split_point = text[0:1023].rfind('\n\n')
                cleaned.append({'source': ("#" + str(count) if first else "-"),
                                'text': entry['text'][0:split_point]})
                text = text[split_point:]
                char_count += 1 if not first else 0
                first = False
            char_count += 1
            cleaned.append({'source': "-",
                            'text': text})
        else:
            cleaned.append({'source': "#" + str(count),
                            'text': entry['text']})
        if char_count > 5500:
            split_embed_at = entries.index(entry)
            char_count = 0
        count += 1

    return cleaned, split_embed_at
