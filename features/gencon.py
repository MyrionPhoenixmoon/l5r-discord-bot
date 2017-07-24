import requests
import re
import datetime


def do_gencon(command):

    def days_till_gencon():
        p = requests.get('http://www.gencon.com')
        pdate = str(re.findall("data-countdown-date='\d+ \w+, \d\d\d\d'",p.text)[0].split('=')[-1]).replace("'",'')
        today = datetime.datetime.today()
        gencon_date = datetime.datetime.strptime(pdate, "%d %B, %Y")
        return str(gencon_date - today).split(',')[0]
    valid_commands = ['days', 'hours', 'minutes', 'seconds', 'parsecs', 'links']
    if command[0] not in valid_commands:
        return "Apologies, but the only thing i know how to do right now is tell you how many days till gencon!"
    else:
        if command[0] == "parsecs":
            return 'http://i.imgur.com/zfPbrGk.gif'
        elif command[0] == "links":
            return "Here's some helpful gencon links! \n"+ \
            "Gencon Home: www.gencon.com \n"+ \
            "/r/l5r's guide to gencon: https://www.reddit.com/r/l5r/comments/5s1ykm/the_l5r_lcg_launches_at_gencon_2017_heres/ \n "+\
            "L5R Gencon Events: http://gencon.eventdb.us/keyword.php?searchBy=legend+of+the+five+rings \n "+ \
            "Map of Downtown Indy: https://goo.gl/maps/6AeZNvHAw5S2"
        else:
            days = int(days_till_gencon().split(' ')[0])
            if command[0] == "days":
                return days + ' till gencon!'
            elif command[0] == "hours":
                return "approximately %s hours till gencon!" % str(days * 24)
            elif command[0] == "minutes":
                return "approximately %s seconds till gencon!" % str(days * 1440)
            elif command[0] == "seconds":
                return "approximately %s seconds till gencon!" % str(days * 86400)
            