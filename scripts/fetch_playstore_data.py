import pandas as pd
from sqlalchemy import create_engine
from google_play_scraper import app, reviews_all
import os
from datetime import datetime

# Define a custom NotFoundError in case the google_play_scraper package doesn't have it
class NotFoundError(Exception):
    pass

# Step 1: Specify the App ID
app_id = 'com.boa.boaMobileBanking'  # Modify as per actual app ID

# Step 2: Fetch App Information and Reviews
try:
    app_info = app(app_id)
    reviews = reviews_all(app_id)
except Exception as e:
    if "404" in str(e):
        raise NotFoundError(f"App not found with ID: {app_id}")
    else:
        raise

# Debugging: Print fetched app information and reviews count
print("App Info:", app_info)
print("Number of Reviews Fetched:", len(reviews))

# Step 3: Filter reviews from 2017 onwards
start_date = datetime(2017, 1, 1)
filtered_reviews = [review for review in reviews if review['at'] >= start_date]

if app_info and filtered_reviews:
    # Step 4: Construct DataFrames
    app_data = {
        'date': pd.Timestamp.now(),
        'installs': app_info.get('installs', 'N/A'),
        'version': app_info.get('version', 'N/A')
    }

    app_data_df = pd.DataFrame([app_data])

    # Debugging: Print app data DataFrame
    print("App Data DataFrame:", app_data_df)

    # Specify the required columns for the reviews DataFrame
    reviews_data = []
    for review in filtered_reviews:
        reviews_data.append({
            'reviewId': review['reviewId'],
            'userName': review['userName'],
            'userImage': review['userImage'],
            'thumbsUp': review['thumbsUpCount'],
            'reviewCreatedVersion': review['reviewCreatedVersion'],
            'at': review['at'],
            'replyContent': review.get('replyContent', ''),
            'repliedAt': review.get('repliedAt', ''),
            'appVersion': review['reviewCreatedVersion'],
            'score': review['score'],
            'content': review['content'],
            'keywords': '',
            'lda_category': '',
            'sentiment': '',
            'insight': ''
        })

    reviews_df = pd.DataFrame(reviews_data)

    # Debugging: Print reviews DataFrame head
    print("Reviews DataFrame head:", reviews_df.head())

    # Ensure the 'data/raw' directory exists
    os.makedirs('data/raw', exist_ok=True)

    # Step 5: Store Data in SQL Tables
    db_host = 'localhost'
    db_port = '5432'
    db_name = 'tickvah_banks_ads'
    db_user = 'postgres'
    db_password = 'admin'

    # Construct the database URL
    db_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

    # Create the SQLAlchemy engine
    engine = create_engine(db_url)

    # Use new table names for storing data
    reviews_df.to_sql('playstore_reviews_info', engine, if_exists='replace', index=False)
    app_data_df.to_sql('playstore_app_info', engine, if_exists='replace', index=False)

    # Step 6: Save Data to CSV Files
    app_data_df.to_csv('data/raw/playstore_app_data.csv', index=False)
    reviews_df.to_csv('data/raw/playstore_reviews.csv', index=False)

    print("Data saved successfully.")
else:
    print("No data to save.")


'''
This script is to count the install count 


'''


import pandas as pd
from sqlalchemy import create_engine
from google_play_scraper import app, reviews_all
import os
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.formula.api import ols

# Define a custom NotFoundError in case the google_play_scraper package doesn't have it
class NotFoundError(Exception):
    pass

# Specify the App ID
app_id = 'com.boa.boaMobileBanking'  # Modify as per actual app ID

# Fetch App Information and Reviews
try:
    app_info = app(app_id)
    reviews = reviews_all(app_id)
except Exception as e:
    if "404" in str(e):
        raise NotFoundError(f"App not found with ID: {app_id}")
    else:
        raise

# Filter reviews from 2017 onwards and aggregate install counts by date
start_date = datetime(2017, 1, 1)
install_count_by_date = {}
for review in reviews:
    if review['at'].date() >= start_date.date():
        date = review['at'].date()
        install_count = review['thumbsUpCount']  # Assuming thumbsUpCount represents install count
        if date in install_count_by_date:
            install_count_by_date[date] += install_count
        else:
            install_count_by_date[date] = install_count

# Convert install_count_by_date dictionary to DataFrame
install_data_df = pd.DataFrame(list(install_count_by_date.items()), columns=['date', 'install_count'])
install_data_df['date'] = pd.to_datetime(install_data_df['date'])
install_data_df = install_data_df.sort_values('date')

# Ensure the 'data/raw' directory exists
os.makedirs('data/raw', exist_ok=True)

# Store Data in SQL Tables
db_host = 'localhost'
db_port = '5432'
db_name = 'tickvah_banks_ads'
db_user = 'postgres'
db_password = 'admin'

# Construct the database URL
db_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

# Create the SQLAlchemy engine
engine = create_engine(db_url)

# Use new table names for storing data
install_data_df.to_sql('daily_install_count', engine, if_exists='replace', index=False)

# Save Data to CSV File
install_data_df.to_csv('data/raw/daily_install_count.csv', index=False)

# Perform regression analysis
model = ols('install_count ~ date', data=install_data_df).fit()
print(model.summary())

print("Data saved and analysis completed successfully.")