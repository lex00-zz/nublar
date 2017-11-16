import requests

API_URL = 'https://jobs.github.com'

class API(object):
    """
    A simple client for the Github Jobs API
    https://jobs.github.com/api
    """

    def __init__(self):
        """Return an Github Jobs API client"""

    def find_positions(self, description=None, location=''):
        """Search the Github Jobs API

        :param str description: Job title
        :param str location: Job location
        :return: JSON object
        :rtype: str
        :raises ValueError: if description is not provided
        """
        if not description:
            raise ValueError("'description' is required")

        positions_url = '{}/positions.json?description={}&location={}'.format(
            API_URL, description, location
        )

        return requests.get(positions_url).json()
