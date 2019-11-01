import requests
import os
import json

import pandas as pd
import altair as alt
from flask import Flask, request, redirect, session, url_for, render_template
from requests_oauthlib import OAuth2Session

# Set up Oura Cloud API credentials
with open('oura_app_credentials.json') as json_file:
    credentials = json.load(json_file)

CLIENT_ID = credentials['CLIENT_ID']
CLIENT_SECRET = credentials['CLIENT_SECRET']
AUTH_URL = 'https://cloud.ouraring.com/oauth/authorize'
TOKEN_URL = 'https://api.ouraring.com/oauth/token'

app = Flask(__name__)

OUTPUT_PATH = 'output/'
TEMPLATES_PATH = 'app/_tutorials/templates/'

dates_to_ignore = pd.to_datetime(['2019-10-23', '2019-10-27', '2019-10-29'])


@app.route('/')
def index():
    """Home page.
    """
    return '<h1>Home page.</h1>'


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
    """Retrieve acces_token from Oura response URL. Redirect to profile page.
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
    oauth_token = session['oauth']['access_token']
    result = requests.get('https://api.ouraring.com/v1/userinfo?access_token=' + oauth_token)
    return str(result.json()) 


@app.route('/summaries')
def summaries():
    """Request data for sleep, activity, and readiness summaries. 
    Save to CSV.
    """
    # Request data
    oauth_token = session['oauth']['access_token']
    summaries = ['sleep', 'activity', 'readiness']

    # Loop through summary types
    for summary in summaries:
        url = 'https://api.ouraring.com/v1/' + summary + '?start=2018-01-01'

        result = requests.get(url, headers={'Content-Type': 'application/json',
                                            'Authorization': 'Bearer {}'
                                            .format(oauth_token)})

        # Convert response JSON to DataFrame
        df = pd.DataFrame(result.json()[summary])
        # Write CSV to output path
        df.to_csv(OUTPUT_PATH + summary + '.csv')

    return '<h1>Successfully requested summary data.</h1>'


@app.route('/plot/<summary>/<varnames>')
def plot(summary='sleep', varnames='rmssd'):
    """Use the Altair library to plot the data indicated by the parsed URL
    parameters.

    <summary> : data category from the summaries list
    <varnames> : column names from csv, separated by a (space) in the URL
    """

    CHART_NAME = 'plot1.html'

    # Read CSV for selected summary
    df = pd.read_csv(
        OUTPUT_PATH + summary + '.csv',
        index_col='summary_date',
        parse_dates=True)[varnames.split(' ')]

    # Drop dates that contain erroneous measurements. (hardcoded, for now)
    df.drop(dates_to_ignore, inplace=True)

    # Create source data structure for Altair plot
    source = df.reset_index().melt('summary_date')

    # Create Altair Chart object
    chart = alt.Chart(source).mark_line().encode(
        x='summary_date:T',
        y='value:Q',
        color='variable',
    ).properties(width=600, height=400)

    # Save chart
    chart.save(TEMPLATES_PATH + CHART_NAME)

    return render_template(CHART_NAME)


def scale_data():
    from sklearn.preprocessing import StandardScaler

    df_subset = df[['awake',
                    'bedtime_end_delta',
                    'bedtime_start_delta',
                    'breath_average', 'deep',
                    'duration', 'efficiency',
                    'hr_average', 'hr_lowest',
                    'period_id', 'rem',
                    'restless', 'rmssd',
                    'score', 'score_alignment',
                    'score_deep',
                    'score_rem', 'score_total',
                    'temperature_delta']]

    scaled_as_array = StandardScaler().fit_transform(df_subset)

    return pd.DataFrame(scaled_as_array, columns=df_subset.columns)


if __name__ == '__main__':

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.secret_key = os.urandom(24)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=False, host='0.0.0.0', port=3030)
