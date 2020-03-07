import requests
from requests.exceptions import HTTPError, Timeout


class NitradoRequests:
    NITRAPI_BASE_URL = "https://api.nitrado.net"
    NITRAPI_GAMESERVER_BOOST_HISTORY = "/services/:id/gameservers/boost/history"
    NITRAPI_GAMESERVER_DETAILS = "/services/:id/gameservers"
    NITRAPI_SERVICES = "/services"

    # Send a Discord API request
    def sendNitrapiRequest(self, action, token, url, params=None):
        # Do request here

        auth_token = f'Bearer {token}'

        try:
            if action == 'GET':
                response = requests.get(url, timeout=5, headers={"Authorization": auth_token})
            elif action == 'POST':
                response = requests.post(url, timeout=5, headers={"Authorization": auth_token}, json=params)
            elif action == 'PATCH':
                response = requests.patch(url, timeout=5, headers={"Authorization": auth_token}, json=params)
            else:
                raise Exception(f'Attempting to send request with unknown action: {action}')

            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred for {id}: {http_err}')
        except Timeout as timeout:
            print(f'HTTP timeout occurred for {id}: {timeout}')
        except Exception as err:
            print(f'Other error occurred for {id}: {err}')
        else:
            return response.json()

        return None

    # Make GET request to NitrAPI for boost history
    # Return: Dict | None
    # See for more info: https://doc.nitrado.net/
    def getBoostHistory(self, token, gameserver_id):
        url = self.NITRAPI_BASE_URL + self.NITRAPI_GAMESERVER_BOOST_HISTORY.replace(':id', gameserver_id, 1)

        return self.sendNitrapiRequest("GET", token, url)

    # Make GET request to NitrAPI for gameserver details
    # Return: Dict | None
    # See for more info: https://doc.nitrado.net/#api-Gameserver-Details
    def getGameserverDetails(self, token, gameserver_id):
        url = self.NITRAPI_BASE_URL + self.NITRAPI_GAMESERVER_DETAILS.replace(':id', gameserver_id, 1)

        return self.sendNitrapiRequest("GET", token, url)

    def getServices(self, token):
        url = self.NITRAPI_BASE_URL + self.NITRAPI_SERVICES

        return self.sendNitrapiRequest("GET", token, url)