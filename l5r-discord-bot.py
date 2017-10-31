import discord
import logging
import json
import collections
import random
import urllib

import features.dice as dice
import features.cards as cards
import features.oracle as oracle
import features.gencon as gencon
import features.rulings as rulings

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='l5r-bot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = discord.Client()

role_numbers_per_server = {}

with open('role_numbers.json', 'r') as json_data:
    try:
        role_numbers_per_server = json.load(json_data)
    except json.decoder.JSONDecodeError:
        role_numbers_per_server = {}
with open('default_roles.json', 'r') as json_data:
    try:
        default_roles = json.load(json_data)
    except json.decoder.JSONDecodeError:
        default_roles = {}
with open('hidden_roles.json', 'r') as json_data:
    try:
        hidden_roles = json.load(json_data)
    except json.decoder.JSONDecodeError:
        hidden_roles = {}
with open('forbidden_roles.json', 'r') as json_data:
    try:
        forbidden_roles = json.load(json_data)
    except json.decoder.JSONDecodeError:
        forbidden_roles = {}


async def save_stats_to_file():
    with open('role_numbers.json', 'w') as outfile:
        json.dump(role_numbers_per_server, outfile)
        logger.info('Saved new role stats to file')

async def save_default_roles_to_file():
    with open('default_roles.json', 'w') as outfile:
        json.dump(default_roles, outfile)
        logger.info('Saved default roles to file')

async def save_hidden_roles_to_file():
    with open('hidden_roles.json', 'w') as outfile:
        json.dump(hidden_roles, outfile)
        logger.info('Saved hidden roles to file')

async def save_forbidden_roles_to_file():
    with open('forbidden_roles.json', 'w') as outfile:
        json.dump(forbidden_roles, outfile)
        logger.info('Saved forbidden roles to file')


async def update_server_stats():
    for server in client.servers:
        stats = collections.Counter()
        for member in server.members:
            roles = [role.name for role in member.roles if role.name != '@everyone']
            stats.update(roles)
        role_numbers_per_server[server.name] = stats
        await save_stats_to_file()

async def reload_from_files():
    global role_numbers_per_server
    global default_roles
    global hidden_roles
    with open('role_numbers.json', 'r') as json_data:
        try:
            role_numbers_per_server = json.load(json_data)
        except json.decoder.JSONDecodeError:
            role_numbers_per_server = {}
    with open('default_roles.json', 'r') as json_data:
        try:
            default_roles = json.load(json_data)
        except json.decoder.JSONDecodeError:
            default_roles = {}
    with open('hidden_roles.json', 'r') as json_data:
        try:
            hidden_roles = json.load(json_data)
        except json.decoder.JSONDecodeError:
            hidden_roles = {}
    with open('forbidden_roles.json', 'r') as json_data:
        try:
            forbidden_roles = json.load(json_data)
        except json.decoder.JSONDecodeError:
            forbidden_roles = {}


@client.event
async def on_ready():
    logger.info('Logged in as')
    logger.info(client.user.name)
    logger.info(client.user.id)
    logger.info('------')

    logger.info('Updating role statistics')
    await update_server_stats()
    await save_stats_to_file()


@client.event
async def on_member_join(new_member):
    logger.info('A new member joined')
    try:
        roles = default_roles[new_member.server]
    except KeyError:
        logger.info('But there are no default roles set up!')
        return None
    client.add_roles(new_member, roles)
    logger.info('Added new roles to ' + new_member.name)

    role_numbers_per_server[new_member.server.name].update(roles)
    await save_stats_to_file()


@client.event
async def on_message(message):
    if message.content.startswith('!help'):
        logger.debug(str(message.author) + " asked for help!")
        help_text = "The Miya Herald has the following Emperor-granted powers: \n" + \
                    "\n" + \
                    "!help informs you about what he may do.  \n" + \
                    "\n" + \
                    "!clan <rolename> lets you swear allegiance to or leave a given clan. \n" + \
                    "!clan <rolename> default lets the admins set default roles that to apply to new members. \n" + \
                    "!clan <rolename> hidden lets the admins hide roles from the output. \n \n" + \
                    "!clans tells you how many people are in each clan. \n \n" + \
                    "!card <cardname> looks up cards on https://fiveringsdb.com \n \n" +\
                    "!oracle <cardname> looks up old5r cards on http://l5rdb.net/ \n \n" +\
                    "!roll is used to roll dice. \n" + \
                    "[] denotes optional elements, {} denotes 'pick one'. show_dice shows the individual dice " + \
                    "results. \n " + \
                    "The following formats are supported: \n \n" + \
                    "!roll XkY [{+-}Z} [TN##] [unskilled] [emphasis] [mastery] [show_dice] rolls X 10-sided " + \
                    "exploding dice and keeps the highest Y. \n" + \
                    "Unskilled can be set to prevent the dice from exploding, while Emphasis rerolls 1s. \n" + \
                    "Mastery allows the dice to explode on 9s and 10s. \n" + \
                    "Ex. !roll 6k3 TN20 or !roll 2k2 TN10 unskilled \n \n" + \
                    "!gencon lets you count down the time until Gencon! \n" + \
                    "!wiki searches the L5R Gameapedia Wiki \n" + \
                    "!report and !stats provide links to win/loss statistics gathering and data"
        await client.send_message(message.channel, help_text)

    if message.content.lower().startswith('!clan') and message.content.lower() != '!clans':
        command = message.content.split(' ')[1:]
        if len(command) == 1:
            logger.info(message.author.name + ' wants to join or leave a clan!')
            # All clan roles are nicely capitalized
            clan_name = command[0].lower().capitalize()
            try:
                forbidden_roles[message.server.name]
            except KeyError:
                forbidden_roles[message.server.name] = []

            if clan_name in forbidden_roles[message.server.name]:
                await client.send_message(message.channel, 'How presumptuous! This is not a clan one can simply ' +
                                          "join!")
            else:
                logger.info('That clan is ' + clan_name)
                role = discord.utils.find(lambda r: r.name == clan_name, message.server.roles)
                if role is None:
                    # lcgplayer and rpgplayer however, aren't, so we must cover that case as well.
                    role = discord.utils.find(lambda r: r.name == clan_name.lower(), message.server.roles)
                if role is not None and role not in message.author.roles:
                    try:
                        await client.add_roles(message.author, role)
                        role_numbers_per_server[message.server.name][role.name] += 1
                        await client.send_message(message.channel, 'Let it be known that ' + message.author.mention +
                                                  ' joined the ' + role.name + ' clan!')
                        if role.name == "Crab":
                            await client.send_message(message.channel, '**CRAAAAAAAAB!**')
                        if role.name == "Dragon":
                            await client.send_message(message.channel, 'What makes a Dragon?')
                        if role.name == "Scorpion":
                            await client.send_message(message.channel, message.author.mention + ' can swim!')
                        if role.name == "Phoenix":
                            await client.send_message(message.channel, 'It has been ~~' + str(random.randint(0, 20)) +
                                                      '~~ 0 days since our last maho incident.')
                        if role.name == "Crane":
                            await client.send_message(message.channel, 'A most excellent choice!')
                        if role.name == "Unicorn":
                            await client.send_message(message.channel, 'Hello Moto!')
                    except discord.errors.Forbidden:
                        logger.info("Got a FORBIDDEN error while adding to the clan")
                        await client.send_message(message.channel, 'How presumptuous! This is not a clan one can simply ' +
                                                  "join! *AKA you're not permitted to join this role or I'm not allowed " +
                                                  "to give it to you*")
                elif role is not None and role in message.author.roles:
                    await client.remove_roles(message.author, role)
                    role_numbers_per_server[message.server.name][role.name] -= 1
                    if role_numbers_per_server[message.server.name][role.name] == 0:
                        del (role_numbers_per_server[message.server.name][role.name])
                    await client.send_message(message.channel, 'Let it be known that ' + message.author.mention +
                                              ' left the ' + role.name + ' clan!')
                else:
                    logger.info("The clan doesn't exist")
                    await client.send_message(message.channel, 'Unfortunately, ' + message.author.mention +
                                              '-san, this clan is not listed in the Imperial Records...')
        elif len(command) == 2:
            if not message.author.server_permissions.manage_server:
                logger.warning(message.author.name + ' tried to set default, hidden or forbidden roles without permission!')
                await client.send_message(message.channel, 'You do not have permission to modify the default or hidden roles.')
                return None
            logger.info(message.author.name + ' wants to manage default or hidden roles.')
            if command[1] == 'default':
                role = discord.utils.find(lambda r: r.name == command[0], message.server.roles)
                try:
                    default_roles[message.server.name]
                except KeyError:
                    default_roles[message.server.name] = []
                if role.name in default_roles[message.server.name]:
                    default_roles[message.server.name].remove(role.name)
                    await save_default_roles_to_file()
                    await client.send_message(message.channel, role.name +
                                              ' has been removed from the default roles list.')
                else:
                    default_roles[message.server.name].append(role.name)
                    await save_default_roles_to_file()
                    await client.send_message(message.channel, role.name + ' has been added to the default roles list.')
            if command[1] == 'hidden':
                role = discord.utils.find(lambda r: r.name == command[0], message.server.roles)
                try:
                    hidden_roles[message.server.name]
                except KeyError:
                    hidden_roles[message.server.name] = []
                if role.name in hidden_roles[message.server.name]:
                    hidden_roles[message.server.name].remove(role.name)
                    await save_hidden_roles_to_file()
                    await client.send_message(message.channel, role.name +
                                              ' has been removed from the hidden roles list.')
                else:
                    hidden_roles[message.server.name].append(role.name)
                    await save_hidden_roles_to_file()
                    await client.send_message(message.channel,
                                              role.name + ' has been added to the hidden roles list.')
            if command[1] == 'forbidden':
                role = discord.utils.find(lambda r: r.name == command[0], message.server.roles)
                try:
                    forbidden_roles[message.server.name]
                except KeyError:
                    forbidden_roles[message.server.name] = []
                if role.name in forbidden_roles[message.server.name]:
                    forbidden_roles[message.server.name].remove(role.name)
                    await save_forbidden_roles_to_file()
                    await client.send_message(message.channel, role.name +
                                              ' has been removed from the forbidden roles list.')
                else:
                    forbidden_roles[message.server.name].append(role.name)
                    await save_forbidden_roles_to_file()
                    await client.send_message(message.channel,
                                              role.name + ' has been added to the forbidden roles list.')
            else:
                await client.send_message(message.channel, 'That is not a request I can fulfill. Perhaps you should ' +
                                          'ask for !help first.')
    if message.content.lower().startswith('!clans'):
        roles = role_numbers_per_server[message.server.name]
        logger.info("Displaying clan numbers")
        try:
            hidden_roles[message.server.name]
        except KeyError:
            hidden_roles[message.server.name] = []
        response = "```"
        for role, count in roles.items():
            if role not in hidden_roles[message.server.name]:
                response += role + ": " + str(count) + "\n"
        response += "``` \n"
        await client.send_message(message.channel, response)
        await update_server_stats()
    if message.content.lower().startswith('!roll'):
        command = message.content.split(' ')[1:]
        if len(command) < 1:
            await client.send_message(message.channel,
                                      "4. Chosen by fair dice roll as the random number. "
                                      "If you wanted something else, perhaps look at !help")
        elif "k" in command[0]:
            roll, success = dice.roll_and_keep(command)
            await client.send_message(message.channel,
                                      message.author.mention + " rolled **" + str(roll) + "**! \n" + success)
        else:
            await client.send_message(message.channel,
                                      "Sorry, samurai-san, I didn't understand your request. \n"
                                      "!help should be informative for you.")
    if message.content.lower().startswith('!card'):
        command = message.content.split(' ')[1:]
        if len(command) < 1:
            await client.send_message(message.channel, "I can look cards up for you, honourable samurai-san, but please tell me which one.")
        else:
            await client.send_message(message.channel, cards.get_card_url(command))
    if message.content.lower().startswith('!oracle'):
        command = message.content.split(' ')[1:]
        if len(command) < 1:
            await client.send_message(message.channel, "I can look Old5r cards up for you, honourable samurai-san.")
        else:
            await client.send_message(message.channel, oracle.get_card_url(command))
    if message.content.lower().startswith('!gencon'):
        command = message.content.split(' ')[1:]
        if len(command) < 1:
            await client.send_message(message.channel, "Say '!gencon COMMAND'. Valid commands are: days, hours, minutes, seconds, parsecs, links")
        else:
            await client.send_message(message.channel, gencon.do_gencon(command))
    if message.content.lower().startswith('!reload'):
        await reload_from_files()
    if message.content.lower().startswith('!report'):
        await client.send_message(message.channel, "<https://goo.gl/forms/aZw0kmvgBhyNc2sI2>")
    if message.content.lower().startswith('!stats'):
        await client.send_message(message.channel, "<https://docs.google.com/spreadsheets/d/e/2PACX-1vQ0HFgzxmgf9hcqIXGniaU3MU8uZjyzd2kAsrDtbHav283sWoY7Z1vc5dOlCz3OpIdwubLkAcovb7Zn/pubhtml>")
    if message.content.lower().startswith('!wiki'):
        command = message.content.split(' ')[1:]
        if len(command) < 1:
            await client.send_message(message.channel, "Here's the wiki: https://l5r.gamepedia.com/")
        else:
            await client.send_message(message.channel, 'https://l5r.gamepedia.com/index.php?search=' + urllib.parse.quote(' '.join(command)))
    if message.content.lower().startswith('!ruling'):
        command = message.content.split(' ')[1:]
        if len(command) < 1:
            await client.send_message(message.channel, "https://fiveringsdb.com/rules/reference")
        else:
            embeds, error_message = rulings.get_rulings(command)
            if embeds is None:
                await client.send_message(message.channel, error_message)
            else:
                for embed in embeds:
                    await client.send_message(message.channel, embed=embed)


client.run('MzE3MjAwMjk5ODQ2NjY0MTky.DAgYmg.L9GPRhrc9HbaFEv2tyS5aG54FOY')
