import pandas as pd
from sqlalchemy import create_engine, text
import matplotlib.pyplot as plt
import seaborn as sns
from db_connection import get_database_engine
import logging

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to load data from PostgreSQL
def load_data(engine):
    try:
        playstore_query = "SELECT * FROM playtore_reviews"
        ads_query = "SELECT * FROM bank_advertisements"
        
        playstore_reviews = pd.read_sql(playstore_query, engine)
        bank_ads = pd.read_sql(ads_query, engine)
        
        return playstore_reviews, bank_ads   
    except Exception as e:
        logger.error(f"Error occurred while loading data from PostgreSQL: {e}")
        return None, None


# Function to preprocess the data
def preprocess_data(playstore_reviews, bank_ads):
    logger.info("Playstore Reviews Columns: " + ", ".join(playstore_reviews.columns))
    logger.info("Bank Ads Columns: " + ", ".join(bank_ads.columns))
    
    # Convert columns to datetime
    playstore_reviews['at'] = pd.to_datetime(playstore_reviews['at'])
    bank_ads['date'] = pd.to_datetime(bank_ads['date'])

    return playstore_reviews, bank_ads

# Function to analyze the impact of ads
def analyze_impact(playstore_reviews, bank_ads):
    results = []
    for _, ad in bank_ads.iterrows():
        ad_date = ad['Date']
        pre_ad_reviews = playstore_reviews[playstore_reviews['at'] < ad_date]
        post_ad_reviews = playstore_reviews[playstore_reviews['at'] >= ad_date]

        pre_ad_count = pre_ad_reviews.shape[0]
        post_ad_count = post_ad_reviews.shape[0]
        
        pre_ad_avg_rating = pre_ad_reviews['score'].mean()
        post_ad_avg_rating = post_ad_reviews['score'].mean()

        results.append({
            'ad_date': ad_date,
            'pre_ad_count': pre_ad_count,
            'post_ad_count': post_ad_count,
            'pre_ad_avg_rating': pre_ad_avg_rating,
            'post_ad_avg_rating': post_ad_avg_rating
        })

    return pd.DataFrame(results)


# Function to visualize the results
def visualize_results(results):
    plt.figure(figsize=(14, 7))
    
    # Plotting number of reviews before and after each ad
    plt.subplot(1, 2, 1)
    sns.barplot(x='ad_date', y='pre_ad_count', data=results, color='blue', label='Before Ad')
    sns.barplot(x='ad_date', y='post_ad_count', data=results, color='red', label='After Ad')
    plt.xlabel('Ad Date')
    plt.ylabel('Number of Reviews')
    plt.title('Number of Reviews Before and After Ads')
    plt.legend()

    # Plotting average rating before and after each ad
    plt.subplot(1, 2, 2)
    sns.barplot(x='ad_date', y='pre_ad_avg_rating', data=results, color='blue', label='Before Ad')
    sns.barplot(x='ad_date', y='post_ad_avg_rating', data=results, color='red', label='After Ad')
    plt.xlabel('Ad Date')
    plt.ylabel('Average Rating')
    plt.title('Average Rating Before and After Ads')
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    engine = get_database_engine(db_name='tickvah_banks_ads', db_user='postgres', db_password='admin', db_host='localhost', db_port='5432')
    playstore_reviews, bank_ads = load_data(engine)
    
    if playstore_reviews is not None and bank_ads is not None:
        playstore_reviews, bank_ads = preprocess_data(playstore_reviews, bank_ads)
        results = analyze_impact(playstore_reviews, bank_ads)
        visualize_results(results)
