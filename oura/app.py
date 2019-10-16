import requests
import os

import pandas as pd
import json
from flask import Flask, request, redirect, session, url_for, render_template
from requests_oauthlib import OAuth2Session
from . import CLIENT_ID, CLIENT_SECRET, TOKEN_URL, DATA_DIR, AUTH_URL,\
                CREDENTIALS, logger, app
from .database import save_to_db_table_from_df


@app.route('/')
def index():
    """Home page with sidebar menu.
    """
    return render_template('index.html')


@app.route('/oura_login')
def oura_login():
    """Redirect to the OAuth provider login page.
    """

    oura_session = OAuth2Session(CLIENT_ID)

    # URL for Oura's authorization page.
    authorization_url, state = oura_session.authorization_url(AUTH_URL)
    session['oauth_state'] = state
    session['record_id'] = 1
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
    result_json = result.json()

    result_json['user_name'] = 'Foo'
    result_json['record_id'] = session['record_id']

    # Write to file
    # fp = DATA_DIR.joinpath('profile.json').as_posix()
    # with open(fp, 'w') as outfile:
    #     json.dump(result.json(), outfile)

    # Write to database
    df = pd.DataFrame(result_json, index=[session['record_id']])
    table_name = 'oura_user_profiles'
    save_to_db_table_from_df(df, CREDENTIALS, table_name, if_exists='replace')

    return render_template('profile.html', content_text=str(result.json()))


@app.route('/summaries')
def summaries():
    """Request data for sleep, activity, and readiness summaries, and either
    write to PostgreSQL database or save as JSON files in `data/`.
    """

    # id to identify user's records in database
    record_id = 0

    # Request data
    oauth_token = session['oauth']['access_token']
    summaries = ['sleep', 'activity', 'readiness']
    for summary in summaries:
        url = 'https://api.ouraring.com/v1/' + summary + '?start=2018-01-01'

        result = requests.get(url, headers={'Content-Type': 'application/json',
                                            'Authorization': 'Bearer {}'
                                            .format(oauth_token)})

        result_json = result.json()

        # Write to file
        # fp = DATA_DIR.joinpath(summary + '.json').as_posix()
        # with open(fp, 'w') as outfile:
        #     json.dump(result_json[summary], outfile)

        # Write to database
        df = pd.DataFrame(result_json[summary])
        table_name = 'oura_' + str(record_id) + '_' + summary
        save_to_db_table_from_df(df, CREDENTIALS, table_name,
                                 if_exists='replace')

    return render_template('summaries.html', content_text=str(result.json()))


@app.route('/export_data', methods=['GET', 'POST'])
def export_data():
    if request.form:
        print(request.form)
    return render_template("profile.html", context_text=str(request.form))


if __name__ == '__main__':

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.secret_key = os.urandom(24)
    app.run(debug=False, host='0.0.0.0', port=3030)
