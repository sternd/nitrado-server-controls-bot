# nitrado-server-controls-bot
A Discord bot to control the status of a Nitrado server

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements.txt

```bash
pip3 install --target ./package -r requirements.txt
PYTHONPATH="PATH_TO_PACKAGE_FOLDER:$PYTHONPATH"
export PYTHONPATH
```

Create copy of "nitrapi_account_config_template.json" as "nitrapi_account_config.json".
Then add the auth_tokens for each of the Nitrado accounts into the config.

Create a copy of ".env_template" as ".env".
Add the values for: DISCORD_TOKEN, DISCORD_GUILD, and DISCORD_CHANNEL

## Docker Build
```bash
docker build -t nitrado-server-controls-bot .
```

## Usage

```bash
docker run nitrado-server-controls-bot
```

## Deployment

## Known Issues

## Contributing
Pull requests are welcome to the "master" branch. For major changes, please open an issue first to discuss what you would like to change.

## License
[GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html)