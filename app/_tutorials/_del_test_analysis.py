import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt



ignore_dates = pd.to_datetime(['2019-10-23', '2019-10-27', '2019-10-29'])

columns_of_interest = ['awake', 'breath_average', 'deep', 'duration',
       'efficiency', 'hr_average', 'hr_lowest', 'rem', 'restless', 'rmssd',
       'score_disturbances', 'score_efficiency', 'score_rem', 'score_total',
       'temperature_delta',  'total']

csvs = [
    'output/activity.csv',
    'output/readiness.csv',
    'output/sleep.csv'
]

df_sleep = pd.read_csv(csvs[2], index_col=[0])


# The sleep and activity summaries have a unique-valued summary date. The sleep
# summary doesn't, since more than one sleep periods (i.e. naps) could occur on the same day.

# Assume single phase of sleep began the date immediately preceding wakeup date.
# Considering that records with a bedtime after midnight would set the sleep_date on the following date.
# Goal is to attain a time series


df_sleep.set_index('summary_date', inplace=True)
df_sleep.drop(index=ignore_dates, inplace=True, errors='ignore')
df = df_sleep[columns_of_interest]

# Plot 1: Average heart rate, lowest heart rate, heart rate variability
source = df[['hr_average', 'hr_lowest', 'rmssd']].reset_index().melt('date')
vega = alt.Chart(source).mark_line().encode(
    x='date',
    y='value',
    color='variable'

).properties(height=400, width=800)
vega.save('a.html')

# Correlation

df.corr(method='spearman').round(2)


pd.to_datetime(df_sleep['summary_date']) == df_sleep.index