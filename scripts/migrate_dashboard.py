# import os
# import pandas as pd
# from sqlalchemy import create_engine
# from google_play_scraper import app, reviews_all
# from datetime import datetime
# import matplotlib.pyplot as plt
# import seaborn as sns
# from statsmodels.formula.api import ols

# # Define a custom NotFoundError in case the google_play_scraper package doesn't have it
# class NotFoundError(Exception):
#     pass

# # Specify the App ID
# app_id = 'com.boa.boaMobileBanking'  # Modify as per actual app ID

# # Fetch App Information and Reviews
# try:
#     app_info = app(app_id)
#     reviews = reviews_all(app_id)
# except Exception as e:
#     if "404" in str(e):
#         raise NotFoundError(f"App not found with ID: {app_id}")
#     else:
#         raise

# # Filter reviews from 2017 onwards and aggregate install counts by date
# start_date = datetime(2017, 1, 1)
# install_count_by_date = {}
# for review in reviews:
#     if review['at'].date() >= start_date.date():
#         date = review['at'].date()
#         install_count = review['thumbsUpCount']  # Assuming thumbsUpCount represents install count
#         if date in install_count_by_date:
#             install_count_by_date[date] += install_count
#         else:
#             install_count_by_date[date] = install_count

# # Convert install_count_by_date dictionary to DataFrame
# install_data_df = pd.DataFrame(list(install_count_by_date.items()), columns=['date', 'install_count'])
# install_data_df['date'] = pd.to_datetime(install_data_df['date'])
# install_data_df = install_data_df.sort_values('date')

# # Ensure the 'data/raw' directory exists
# os.makedirs('data/raw', exist_ok=True)

# # Store Data in SQL Tables
# db_host = 'localhost'
# db_port = '5432'
# db_name = 'tickvah_banks_ads'
# db_user = 'postgres'
# db_password = 'admin'

# # Construct the database URL
# db_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

# # Create the SQLAlchemy engine
# engine = create_engine(db_url)

# # Use new table names for storing data
# install_data_df.to_sql('daily_install_count', engine, if_exists='replace', index=False)

# # Save Data to CSV File
# install_data_df.to_csv('data/raw/daily_install_count.csv', index=False)

# # Perform regression analysis
# model = ols('install_count ~ date', data=install_data_df).fit()
# print(model.summary())

# print("Data saved and analysis completed successfully.")

# from google_play_scraper import app
# app_id = 'com.boa.boaMobileBanking'
# app_info = app(app_id)
# print(app_info)

from google_play_scraper import app
import pandas as pd
from datetime import datetime, timedelta

# Specify the App ID
app_id = 'com.boa.boaMobileBanking'

# Start date
start_date = datetime(2017, 1, 1)

# End date (current date)
end_date = datetime.now()

# Initialize dictionary to store install counts
install_count_by_date = {}

# Loop through each day from start date to end date
current_date = start_date
while current_date <= end_date:
    # Fetch App Information for the current date
    app_info = app(app_id,date=current_date.strftime('%Y-%m-%d'))

    # Extract Install Count
    install_count = app_info['minInstalls'] if 'minInstalls' in app_info else None

    # Store install count in dictionary
    install_count_by_date[current_date.strftime('%Y-%m-%d')] = install_count

    # Move to the next day
    current_date += timedelta(days=1)

# Convert install_count_by_date dictionary to DataFrame
install_data_df = pd.DataFrame(list(install_count_by_date.items()), columns=['date', 'install_count'])
install_data_df['date'] = pd.to_datetime(install_data_df['date'])

# Save Data to CSV File
install_data_df.to_csv('install_counts_daily.csv', index=False)

print("Data saved successfully.")
