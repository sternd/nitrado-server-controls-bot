# bot.py
import os

import discord
from dotenv import load_dotenv
import json
from datetime import datetime
from utils.NitradoRequests import NitradoRequests

load_dotenv(dotenv_path='../config/.env')

TOKEN = os.getenv('DISCORD_TOKEN')
BOT_CLIENT_ID = os.getenv('BOT_CLIENT_ID')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
COMMANDS_FILE = './configs/commands.json'


class CommandHandler:

    # constructor
    def __init__(self, client):
        self.client = client
        self.commands = []
        self.prefix = None

    def add_command(self, command):
        self.commands.append(command)

    def set_prefix(self, prefix):
        self.prefix = prefix

    def command_handler(self, message):
        if not message.content.startswith(self.prefix):
            return None

        for command in self.commands:
            args = message.content.split(' ')
            if args[0] == self.prefix + command['trigger']:
                args.pop(0)
                if command['arg_num'] == 0:
                    return self.client.send_message(message.channel, None, embed=command['function'](message, self.client, args))
                    break
                else:
                    if len(args) >= command['arg_num']:
                        return self.client.send_message(message.channel, None, embed=command['function'](message, self.client, args))
                        break
                    else:
                        return self.client.send_message(message.channel, 'command "{}" requires {} argument(s) "{}"'.format(self.prefix + command['trigger'], command['arg_num'], ', '.join(command['arg_names'])))
                        break
            else:
                break


client = discord.Client()

ch = CommandHandler(client)


def get_nitrado_config():
    with open('../config/nitrapi_account_config.json') as json_file:
        nitrapi_account_config = json.load(json_file)

    return json.loads(nitrapi_account_config)


def get_nitrado_gameserver_by_name(gameserver_name, nitrado_config):
    for account in nitrado_config['nitrado_accounts']:
        auth_token = account["auth_token"]

        for gameserver in account['gameservers']:
            if gameserver['gameserver_name'].lower() == gameserver_name.lower():
                return {
                    "auth_token": auth_token,
                    "gameserver": gameserver
                }

    return None


def load_commands():
    with open('../config/commands.json') as json_file:
        commands = json.load(json_file)

    if 'base_trigger' not in commands:
        print('Missing base trigger in commands.json')
        exit()

    if 'commands' not in commands:
        print('Missing commands in commands.json')
        exit()

    for command in commands['commands']:
        ch.add_command(command)

    print('Commands loaded')


def bot_status(message, client, args):
    embed_params = {
        "embed_title": message,
        "description": None,
        "lines": [
            {
                "title": "Bot Status",
                "message": "Available",
                'inline': False
            }
        ],
        "color": discord.Color('0x7ed321'),
        "requested_by": {
            "name": message.author.name,
            "icon": message.author.avatar_url
        }
    }
    embed = generate_embed(embed_params)

    return embed.to_dict()


def generate_embed(embed_params):
    embed = discord.Embed(
        title=embed_params['embed_title'],
        url="https://github.com/sternd/nitrado-server-controls-bot"
    )

    if embed_params['description'] is not None:
        embed.__setattr__('description', datetime.utcnow())

    if embed_params['color'] is not None:
        embed.__setattr__('colour', embed_params['color'])

    if embed_params['lines']:
        for line in embed_params['lines']:
            embed.add_field(name=line['title'], value=line['message'], inline=line['inline'])

    requestor_name = embed_params['requested_by']['name']
    requestor_icon = embed_params['requested_by']['icon']

    embed.set_footer(text=f'Run by: {requestor_name}',
                     icon_url=requestor_icon)

    return embed


@client.event
async def on_ready():
    try:
        print(f'Nitrado server controls bot is ready: {client.user.name} {client.user.id}')
        load_commands()
    except Exception as e:
        print(e)


@client.event
async def on_message(message):
    # if the message is from a bot, ignore it
    if message.author.bot:
        pass
    else:
        # try to evaluate with the command handler
        try:
            await ch.command_handler(message)
        # message doesn't contain a command trigger
        except TypeError as e:
            pass
        # generic python error
        except Exception as e:
            print(e)


# Start Discord bot
client.run(TOKEN)
