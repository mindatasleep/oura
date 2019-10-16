import logging
import os
import pathlib
import json
from flask import Flask


app = Flask(__name__)


# Set up basic logging
def _get_logger():
    logging.basicConfig(
        level=logging.WARN,
        format='%(name)-24s: %(levelname)-8s %(message)s',)

    return logging.getLogger(f'OURA ERROR LOG::')


LOGLEVEL = os.getenv('LOGLEVEL', 'DEBUG').upper()
logger = _get_logger()
logger.setLevel(LOGLEVEL)
logger2 = logging.getLogger(f'OURA ERROR LOG::')


# Set up Oura Cloud API credentials
with open('oura_app_credentials.json') as json_file:
    credentials = json.load(json_file)

CLIENT_ID = credentials['CLIENT_ID']
CLIENT_SECRET = credentials['CLIENT_SECRET']
AUTH_URL = 'https://cloud.ouraring.com/oauth/authorize'
TOKEN_URL = 'https://api.ouraring.com/oauth/token'


# Set up PostgreSQL credentials
CREDENTIALS = dict(user='',
                   password='',
                   host='127.0.0.1',
                   port='5432',
                   database='oura')


# Set up directory to store data
DATA_DIR = pathlib.Path(os.getenv('DATA_DIR', './data'))
