
def get_card_url(command):

    card_name = ''

    for string in command:
        string.replace("'", "-")
        if card_name != '':
            card_name += '-'
        card_name += string.lower()

    return "https://fiveringsdb.com/bundles/card_images/" + card_name + ".png"