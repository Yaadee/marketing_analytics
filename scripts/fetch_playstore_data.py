import pandas as pd
from sqlalchemy import create_engine
from google_play_scraper import app, reviews_all
import os
from datetime import datetime, timedelta

# Define a custom NotFoundError in case the google_play_scraper package doesn't have it
class NotFoundError(Exception):
    pass

# Function to convert install string to number
def parse_install_count(install_str):
    return int(install_str.replace(',', '').replace('+', ''))

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
    total_installs = parse_install_count(app_info.get('installs', '0'))

    # Specify the required columns for the reviews DataFrame
    reviews_data = []
    for review in filtered_reviews:
        reviews_data.append({
            'reviewId': review['reviewId'],
            'userName': review['userName'],
            'userImage': review['userImage'],
            '👍': review['thumbsUpCount'],
            'reviewCreatedVersion': review['reviewCreatedVersion'],
            'at': review['at'],
            'replyContent': review.get('replyContent', ''),
            'repliedAt': review.get('repliedAt', ''),
            'appVersion': review['reviewCreatedVersion'],
            'score': review['score'],
            'Comments': review['content'],
            'Keywords': '',
            'LDA_Category': '',
            'Sentiment': '',
            'Insight': '',
            'installs': total_installs,
            'date': pd.Timestamp.now(),
            'version': app_info.get('version', 'N/A')
        })

    reviews_df = pd.DataFrame(reviews_data)

    # Debugging: Print reviews DataFrame head
    print("Reviews DataFrame head:", reviews_df.head())

    # Step 5: Aggregate daily review counts as proxy for install counts
    reviews_df['date'] = reviews_df['at'].dt.date  # Extract the date part from 'at'
    daily_review_counts = reviews_df.groupby('date').size().reset_index(name='daily_reviews_count')

    # Create a complete date range from 2017 to now
    date_range = pd.date_range(start=start_date, end=datetime.now().date())
    daily_counts = pd.DataFrame(date_range, columns=['date'])
    
    # Merge with the daily review counts
    daily_counts = pd.merge(daily_counts, daily_review_counts, on='date', how='left').fillna(0)

    # Estimate daily installs based on reviews; this is a simple proxy
    total_reviews = daily_counts['daily_reviews_count'].sum()
    if total_installs > 0 and total_reviews > 0:
        install_ratio = total_installs / total_reviews
        daily_counts['daily_installs_count'] = daily_counts['daily_reviews_count'] * install_ratio
    else:
        daily_counts['daily_installs_count'] = 0

    # Calculate cumulative installs starting from 2017
    daily_counts['cumulative_installs'] = daily_counts['daily_installs_count'].cumsum()

    # Ensure the 'data/raw' directory exists
    os.makedirs('data/raw', exist_ok=True)

    # Step 6: Store Data in SQL Tables
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
    app_data_df = pd.DataFrame([{
        'date': pd.Timestamp.now(),
        'installs': total_installs,
        'version': app_info.get('version', 'N/A')
    }])
    app_data_df.to_sql('playstore_app_info', engine, if_exists='replace', index=False)
    daily_counts.to_sql('daily_review_counts', engine, if_exists='replace', index=False)

    # Step 7: Save Data to CSV Files
    reviews_df.to_csv('data/raw/playstore_reviews.csv', index=False)
    daily_counts.to_csv('data/raw/daily_review_counts.csv', index=False)

    print("Data saved successfully.")
else:
    print("No data to save.")






'''
This script is to count the install count 


'''
import csv
import datetime
from google_play_scraper import app  # Make sure you have installed google_play_scraper

CSV_FILE = 'data/raw/installations.csv'

def init_csv():
    with open(CSV_FILE, 'w', newline='') as csvfile:
        fieldnames = ['date', 'installation_count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

def fetch_installation_count(date):
    with open(CSV_FILE, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['date'] == date.isoformat():
                return int(row['installation_count'])
    return 0  # Return 0 if the count for the given date is not found

def save_installation_count_for_date(date, count):
    with open(CSV_FILE, 'a+', newline='') as csvfile:
        fieldnames = ['date', 'installation_count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Check if the date already exists in the CSV file
        csvfile.seek(0)
        reader = csv.DictReader(csvfile)
        found = False
        for row in reader:
            if row['date'] == date.isoformat():
                # If date exists, update the installation count by adding the new count
                count += int(row['installation_count'])
                found = True
                break

        if not found:
            # If date does not exist, write the count for the date
            csvfile.seek(0, 2)  # Move to the end of the file

        writer.writerow({'date': date.isoformat(), 'installation_count': count})
    print("Installation count saved successfully for", date)

if __name__ == '__main__':
    init_csv()
    app_id = 'com.boa.boaMobileBanking'  
    start_date = datetime.date(2017, 1, 1)
    current_date = start_date
    while current_date <= datetime.date.today():
        try:
            playstore_data = app(app_id)
            installs = playstore_data['realInstalls']
        except Exception as e:
            print(f"Failed to fetch data for {app_id}: {e}")
            installs = 0
        count = fetch_installation_count(current_date) + installs
        save_installation_count_for_date(current_date, count)
        current_date += datetime.timedelta(days=1)