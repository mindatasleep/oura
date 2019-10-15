import requests
import pathlib
import os

from flask import Flask, request, redirect, session, url_for, render_template
from requests_oauthlib import OAuth2Session
import json


with open('oura_app_credentials.json') as json_file:
    credentials = json.load(json_file)

CLIENT_ID = credentials['CLIENT_ID']
CLIENT_SECRET = credentials['CLIENT_SECRET']
AUTH_URL = 'https://cloud.ouraring.com/oauth/authorize'
TOKEN_URL = 'https://api.ouraring.com/oauth/token'

DATA_DIR = pathlib.Path(os.getenv('DATA_DIR', './data'))

app = Flask(__name__)


@app.route('/')
def index():
    """Home page."""
    return render_template("index.html")


@app.route('/oura_login')
def oura_login():
    """Redirect to the OAuth provider login page.
    """

    oura_session = OAuth2Session(CLIENT_ID)

    # URL for Oura's authorization page.
    authorization_url, state = oura_session.authorization_url(AUTH_URL)
    session['oauth_state'] = state
    return redirect(authorization_url)


@app.route('/callback')
def callback():
    """Retrieve acces_token from Oura response url. Redirect to profile page.
    """

    oura_session = OAuth2Session(CLIENT_ID, state=session['oauth_state'])
    session['oauth'] = oura_session.fetch_token(
                        TOKEN_URL,
                        client_secret=CLIENT_SECRET,
                        authorization_response=request.url)

    return redirect(url_for('.profile'))


@app.route('/profile')
def profile():
    """User profile.
    """

    # Request data
    oauth_token = session['oauth']['access_token']
    result = requests.get(
        'https://api.ouraring.com/v1/userinfo?access_token=' + oauth_token)

    # Write to file
    fp = DATA_DIR.joinpath('profile.json').as_posix()
    with open(fp, 'w') as outfile:
        json.dump(result.json(), outfile)

    return str(result.json())


@app.route('/summaries')
def summaries():
    """Request data for sleep, activity, and readiness summaries, and either 
    write to PostgreSQL database or save as JSON files in `data/`.
    """

    # Request data
    oauth_token = session['oauth']['access_token']
    summaries = ['sleep', 'activity', 'readiness']
    for data_type in summaries:
        url = 'https://api.ouraring.com/v1/' + data_type + '?start=2018-01-01'

        result = requests.get(url, headers={'Content-Type': 'application/json',
                                            'Authorization': 'Bearer {}'
                                            .format(oauth_token)})

        # Write to file
        fp = DATA_DIR.joinpath(data_type + '.json').as_posix()
        with open(fp, 'w') as outfile:
            json.dump(result.json(), outfile)

    return str(result.json())


if __name__ == '__main__':

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.secret_key = os.urandom(24)
    app.run(debug=False, host='0.0.0.0', port=3030)
