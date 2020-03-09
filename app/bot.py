# bot.py
import os

import discord as discord
from dotenv import load_dotenv
import json
from datetime import datetime
from NitradoRequests import NitradoRequests

load_dotenv(dotenv_path='./config/.env')

TOKEN = os.getenv('DISCORD_TOKEN')
BOT_CLIENT_ID = os.getenv('BOT_CLIENT_ID')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
COMMANDS_FILE = './configs/commands.json'

COMMAND_FUNCTIONS = {}

DISCORD_GREEN = 0x7ed321
DISCORD_YELLOW = 0xf8e71c
DISCORD_RED = 0xd0021b
DISCORD_WHITE = 0xffffff


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
                if not command['enabled']:
                    embed = command_disabled(message, self.client, args)
                    return message.channel.send(embed=embed)
                args.pop(0)
                if command['arg_num'] == 0:
                    embed = COMMAND_FUNCTIONS[command['function']](message, self.client, args)
                    return message.channel.send(embed=embed)
                else:
                    if len(args) >= command['arg_num']:
                        embed = COMMAND_FUNCTIONS[command['function']](message, self.client, args)
                        return message.channel.send(embed=embed)
                    else:
                        embed = command_error(message, self.client, args, command)
                        return message.channel.send(embed=embed)


client = discord.Client()

ch = CommandHandler(client)


def get_nitrado_config():
    with open('./config/nitrapi_account_config.json') as json_file:
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
    with open('./config/commands.json') as json_file:
        commands = json.load(json_file)

    if 'base_trigger' not in commands:
        print('Missing base trigger in commands.json')
        exit()

    ch.set_prefix(commands['base_trigger'])

    if 'commands' not in commands:
        print('Missing commands in commands.json')
        exit()

    for command in commands['commands']:
        ch.add_command(command)

    print('Commands loaded')


def bot_status(message, client, args):
    print(f'Executed: {message.content}')
    embed_params = {
        "embed_title": message.content,
        "description": None,
        "lines": [
            {
                "title": "Bot Status",
                "message": "Available",
                'inline': False
            }
        ],
        "color": discord.Color(DISCORD_GREEN),
        "requested_by": {
            "name": message.author.name,
            "icon": message.author.avatar_url
        }
    }

    embed = generate_embed(embed_params)

    return embed


COMMAND_FUNCTIONS["bot_status"] = bot_status

def gameserver_status(message, client, args):
    print(f'Executed: {message.content}')
    gameserver_credentials = get_gameserver_credentials(args[0])

    if not gameserver_credentials:
        error_embed_params = generate_error_embed_params(message, 'Gameserver Status', DISCORD_RED, 'No gameserver credentials')
        return generate_embed(error_embed_params)

    auth_token = gameserver_credentials['auth_token']
    gameserver_id = gameserver_credentials['gameserver_id']

    nitrapi = NitradoRequests()
    gameserver_details = nitrapi.getGameserverDetails(auth_token, gameserver_id)

    if not gameserver_details:
        error = 'Gameserver status request failed'
        print(error)
        error_embed_params = generate_error_embed_params(message, 'Gameserver Status', DISCORD_RED, error)
        return generate_embed(error_embed_params)

    if 'data' not in gameserver_details:
        error = 'No gameserver data in response'
        print(error)
        error_embed_params = generate_error_embed_params(message, 'Gameserver Status', DISCORD_RED, error)
        return generate_embed(error_embed_params)

    if 'gameserver' not in gameserver_details['data']:
        error = 'No gameserver details in response'
        print(error)
        error_embed_params = generate_error_embed_params(message, 'Gameserver Status', DISCORD_RED, error)
        return generate_embed(error_embed_params)

    if 'status' not in gameserver_details['data']['gameserver']:
        error = 'No gameserver status in gameserver details'
        print(error)
        error_embed_params = generate_error_embed_params(message, 'Gameserver Status', DISCORD_RED, error)
        return generate_embed(error_embed_params)

    if gameserver_details['data']['gameserver']['status'] == 'started':
        color = DISCORD_GREEN
    elif gameserver_details['data']['gameserver']['status'] == 'restarting':
        color = DISCORD_YELLOW
    else:
        color = DISCORD_RED

    line_value = 'Status: ' + '**' + gameserver_details['data']['gameserver']['status'] + '**'

    if 'query' in gameserver_details['data']['gameserver']:
        if 'player_current' in gameserver_details['data']['gameserver']['query'] and 'player_max' in gameserver_details['data']['gameserver']['query']:
            line_value = line_value + '\nPlayers: ' + '**' + str(gameserver_details['data']['gameserver']['query']['player_current']) + '/' + str(gameserver_details['data']['gameserver']['query']['player_max']) + '**'

    line = generate_embed_line(gameserver_credentials['gameserver_name'], line_value)
    embed_params = generate_embed_params(message, "Gameserver Status", color, [line])

    return generate_embed(embed_params)


COMMAND_FUNCTIONS["gameserver_status"] = gameserver_status


def gameserver_restart(message, client, args):
    print(f'Executed: {message.content}')
    gameserver_credentials = get_gameserver_credentials(args[0])
    gameserver_name = gameserver_credentials['gameserver_name']

    if not gameserver_credentials:
        error_embed_params = generate_error_embed_params(message, f'{gameserver_name} Restart', DISCORD_RED, 'No gameserver credentials')
        return generate_embed(error_embed_params)

    auth_token = gameserver_credentials['auth_token']
    gameserver_id = gameserver_credentials['gameserver_id']

    nitrapi = NitradoRequests()
    # response = nitrapi.restartGameserver(auth_token, gameserver_id)

    #TODO: FOR TESTING. REMOVE THIS!
    response = {"status": "success", "message": "Server will be restarted now."}

    if not response:
        error = 'Error restarting the gameserver'
        print(error)
        error_embed_params = generate_error_embed_params(message, f'{gameserver_name} Restart', DISCORD_RED, error)
        return generate_embed(error_embed_params)

    if 'status' not in response or response['status'] != 'success':
        if 'message' not in response:
            error = 'Error restarting service: ' + response['status']
        else:
            error = 'Error restarting service: ' + response['message']

        print(error)
        error_embed_params = generate_error_embed_params(message, f'{gameserver_name} Restart', DISCORD_RED, error)
        return generate_embed(error_embed_params)

    line = generate_embed_line("Action", "Restart has been requested")
    embed_params = generate_embed_params(message, f'{gameserver_name} Restart', DISCORD_GREEN, [line])
    embed = generate_embed(embed_params)

    return embed


COMMAND_FUNCTIONS["gameserver_restart"] = gameserver_restart


def gameserver_shutdown(message, client, args):
    print(f'Executed: {message.content}')
    gameserver_credentials = get_gameserver_credentials(args[0])
    gameserver_name = gameserver_credentials['gameserver_name']

    if not gameserver_credentials:
        error_embed_params = generate_error_embed_params(message, f'{gameserver_name} Shutdown', DISCORD_RED, 'No gameserver credentials')
        return generate_embed(error_embed_params)

    auth_token = gameserver_credentials['auth_token']
    gameserver_id = gameserver_credentials['gameserver_id']

    nitrapi = NitradoRequests()
    # response = nitrapi.stopGameserver(auth_token, gameserver_id)

    #TODO: FOR TESTING. REMOVE THIS!
    response = {"status": "success", "message": "Server will be shutdown now."}

    if not response:
        error = 'Error shutting down the gameserver'
        print(error)
        error_embed_params = generate_error_embed_params(message, f'{gameserver_name} Shutdown', DISCORD_RED, error)
        return generate_embed(error_embed_params)

    if 'status' not in response or response['status'] != 'success':
        if 'message' not in response:
            error = 'Error shutting down service: ' + response['status']
        else:
            error = 'Error shutting down service: ' + response['message']

        print(error)
        error_embed_params = generate_error_embed_params(message, f'{gameserver_name} Shutdown', DISCORD_RED, error)
        return generate_embed(error_embed_params)

    line = generate_embed_line("Action", "Shutdown has been requested")
    embed_params = generate_embed_params(message, f'{gameserver_name} Shutdown', DISCORD_GREEN, [line])
    embed = generate_embed(embed_params)

    return embed


COMMAND_FUNCTIONS["gameserver_shutdown"] = gameserver_shutdown


def gameserver_start(message, client, args):
    print(f'Executed: {message.content}')
    gameserver_credentials = get_gameserver_credentials(args[0])
    gameserver_name = gameserver_credentials['gameserver_name']

    if not gameserver_credentials:
        error_embed_params = generate_error_embed_params(message, f'{gameserver_name} Start', DISCORD_RED, 'No gameserver credentials')
        return generate_embed(error_embed_params)

    auth_token = gameserver_credentials['auth_token']
    gameserver_id = gameserver_credentials['gameserver_id']

    nitrapi = NitradoRequests()
    # response = nitrapi.restartGameserver(auth_token, gameserver_id)

    #TODO: FOR TESTING. REMOVE THIS!
    response = {"status": "success", "message": "Server will be started now."}

    if not response:
        error = 'Error starting the gameserver'
        print(error)
        error_embed_params = generate_error_embed_params(message, f'{gameserver_name} Start', DISCORD_RED, error)
        return generate_embed(error_embed_params)

    if 'status' not in response or response['status'] != 'success':
        if 'message' not in response:
            error = 'Error starting service: ' + response['status']
        else:
            error = 'Error starting service: ' + response['message']

        print(error)
        error_embed_params = generate_error_embed_params(message, f'{gameserver_name} Start', DISCORD_RED, error)
        return generate_embed(error_embed_params)

    line = generate_embed_line("Action", "Start has been requested")
    embed_params = generate_embed_params(message, f'{gameserver_name} Start', DISCORD_GREEN, [line])
    embed = generate_embed(embed_params)

    return embed


COMMAND_FUNCTIONS["gameserver_start"] = gameserver_start


def bot_help(message, client, args):
    lines = []

    for command in ch.commands:
        usage = "**Usage:** " + ch.prefix + command['trigger'] + " ".join(command['arg_names']) + '\n'
        examples = ""
        for example in command['examples']:
            examples += f'**Example:** {ch.prefix}{example}\n'

        lines.append(generate_embed_line(command['description'], usage + examples))

    embed_params = generate_embed_params(message, "Help Information", DISCORD_WHITE, lines)
    return generate_embed(embed_params)


COMMAND_FUNCTIONS["bot_help"] = bot_help


def command_disabled(message, client, args):
    error = message.content
    error_embed_params = generate_error_embed_params(message, 'Command Disabled', DISCORD_RED, error)
    return generate_embed(error_embed_params)


def command_error(message, client, args, command):
    error = 'command "{}" requires {} argument(s) "{}"'.format(ch.prefix + command['trigger'], command['arg_num'], ', '.join(command['arg_names']))
    error_embed_params = generate_error_embed_params(message, 'Error Using Command', DISCORD_RED, error)
    return generate_embed(error_embed_params)


def get_gameserver_credentials(server_name):
    formatted_server_name = server_name.replace("_", " ").lower()

    for account in NITRADO_CONFIG['nitrado_accounts']:
        auth_token = account['auth_token']

        for gameserver in account['gameservers']:
            if gameserver['gameserver_name'].lower() == formatted_server_name:
                return {
                    "auth_token": auth_token,
                    "gameserver_id": gameserver['gameserver_id'],
                    "gameserver_name": gameserver['gameserver_name']
                }

    return None


def generate_embed_line(title, value, inline=False):
    return {
        "title": title,
        "message": value,
        "inline": inline
    }

def generate_embed_params(message, title, color, lines):
    embed_params = {
        "embed_title": title,
        "description": None,
        "lines": lines,
        "color": discord.Color(color),
        "requested_by": {
            "name": message.author.name,
            "icon": message.author.avatar_url
        }
    }

    return embed_params


def generate_error_embed_params(message, title, color, error):
    embed_params = {
        "embed_title": title,
        "description": None,
        "lines": [
            {
                "title": "ERROR",
                "message": error,
                'inline': False
            }
        ],
        "color": discord.Color(color),
        "requested_by": {
            "name": message.author.name,
            "icon": message.author.avatar_url
        }
    }

    return embed_params


def generate_embed(embed_params):
    embed = discord.Embed(
        title=embed_params['embed_title'],
        url="https://github.com/sternd/nitrado-server-controls-bot"
    )

    if embed_params['description'] is not None:
        embed.__setattr__('description', embed_params["description"])

    if embed_params['color'] is not None:
        embed.__setattr__('colour', embed_params['color'])

    if embed_params['lines']:
        for line in embed_params['lines']:
            embed.add_field(name=line['title'], value=line['message'], inline=line['inline'])

    requestor_name = embed_params['requested_by']['name']
    requestor_icon = embed_params['requested_by']['icon']

    embed.set_footer(text=f'{requestor_name}',
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


NITRADO_CONFIG = get_nitrado_config()

# Start Discord bot
client.run(TOKEN)
