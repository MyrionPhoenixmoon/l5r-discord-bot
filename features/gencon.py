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
    valid_commands = ['days']
    if command[0] not in valid_commands:
        return "Apologies, but the only thing i know how to do right now is tell you how many days till gencon!"
    else:
        if command[0] == "days":
            return days_till_gencon()+' till gencon!'