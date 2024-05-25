import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import json

# Load data
tickvah_ads = pd.read_csv('data/processed/tickvah_ads_processed.csv')
App_install = pd.read_csv('data/processed/App_install_processed.csv')
telegramsubscription = pd.read_csv('data/processed/telegramsubscription_processed.csv')
playstorereviews = pd.read_csv('data/processed/playstorereviews_processed.csv')

# Initialize Dash app
app = dash.Dash(__name__)

# Ad Performance Dashboard
ad_performance_dashboard = html.Div([
    html.H1('Ad Performance Dashboard'),
    dcc.Graph(figure=px.line(tickvah_ads, x='date', y='impressions'))
])

# Ads vs. Download Dashboard
ads_vs_download_dashboard = html.Div([
    html.H1('Ads vs. Download Dashboard'),
    dcc.Graph(figure=px.line(App_install, x='date', y='install_count'))
])

# Ads vs. Subscription Dashboard
ads_vs_subscription_dashboard = html.Div([
    html.H1('Ads vs. Subscription Dashboard'),
    dcc.Graph(figure=px.line(telegramsubscription, x='date', y='subscribers'))
])

# Review Sentiment Dashboard
review_sentiment_dashboard = html.Div([
    html.H1('Review Sentiment Dashboard'),
    dcc.Graph(figure=px.line(playstorereviews, x='at', y='positive', color='sentiment'))
])

# Define app layout
app.layout = html.Div([
    ad_performance_dashboard,
    ads_vs_download_dashboard,
    ads_vs_subscription_dashboard,
    review_sentiment_dashboard
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
