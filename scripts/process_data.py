import pandas as pd
from textblob import TextBlob
import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose
import os

# Function to perform sentiment analysis using TextBlob
def get_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0:
        return 'positive'
    elif polarity < 0:
        return 'negative'
    else:
        return 'neutral'

# Function to extract keywords from text using TextBlob
def extract_keywords(text):
    blob = TextBlob(text)
    keywords = blob.noun_phrases
    keywords_str = ', '.join(keywords)
    return keywords_str

# Function to generate insights based on sentiment
def generate_insight(sentiment):
    if sentiment == 'positive':
        return 'Positive feedback received.'
    elif sentiment == 'negative':
        return 'Negative feedback identified.'
    else:
        return 'Neutral sentiment observed.'

# Database connection parameters
db_config = {
    'dbname': 'tickvah_banks_ads',
    'user': 'postgres',
    'password': 'admin',
    'host': 'localhost',
    'port': '5432'
}

# Create a connection to the PostgreSQL database
conn = psycopg2.connect(
    dbname=db_config['dbname'],
    user=db_config['user'],
    password=db_config['password'],
    host=db_config['host'],
    port=db_config['port']
)

# Create a cursor object using the connection
cur = conn.cursor()

# Example queries to load data from tables
queries = [
    "SELECT * FROM bank_advertisements",
    "SELECT * FROM daily_install_count",
    "SELECT * FROM telegram_subscriptions",
    "SELECT * FROM playstore_reviews_info",
    "SELECT * FROM real_install_count"
]

# Empty list to hold DataFrames
dfs = []

# Execute the queries and fetch all results for each table
for query in queries:
    cur.execute(query)
    data = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    df = pd.DataFrame(data, columns=column_names)
    dfs.append(df)

# Close cursor and connection
cur.close()
conn.close()

# Now you have separate DataFrames for each table
tickvah_ads = dfs[0]
App_install = dfs[1]
telegramsubscription = dfs[2]
playstorereviews = dfs[3]
real_install = dfs[4]

# Apply keyword extraction and sentiment analysis functions to 'content' column
playstorereviews['keywords'] = playstorereviews['content'].apply(extract_keywords)
playstorereviews['sentiment'] = playstorereviews['content'].apply(get_sentiment)

# Generate insights based on sentiment
playstorereviews['insight'] = playstorereviews['sentiment'].apply(generate_insight)

# Re-establish connection to the PostgreSQL database to update the table
conn = psycopg2.connect(
    dbname=db_config['dbname'],
    user=db_config['user'],
    password=db_config['password'],
    host=db_config['host'],
    port=db_config['port']
)

# Create a cursor object using the connection
cur = conn.cursor()

# Update the table with sentiment, keywords, and insight information
update_query = """
    UPDATE playstore_reviews_info
    SET sentiment = %s, keywords = %s, insight = %s
    WHERE "reviewId" = %s
"""

for index, row in playstorereviews.iterrows():
    sentiment = row['sentiment']
    keywords = row['keywords']
    insight = row['insight']
    reviewId = row['reviewId']
    cur.execute(update_query, (sentiment, keywords, insight, reviewId))

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()

# Save processed data to CSV
data_processed_dir = 'data/processed'
if not os.path.exists(data_processed_dir):
    os.makedirs(data_processed_dir)

tickvah_ads.to_csv(os.path.join(data_processed_dir, 'tickvah_ads_processed.csv'), index=False)
App_install.to_csv(os.path.join(data_processed_dir, 'App_install_processed.csv'), index=False)
telegramsubscription.to_csv(os.path.join(data_processed_dir, 'telegramsubscription_processed.csv'), index=False)
playstorereviews.to_csv(os.path.join(data_processed_dir, 'playstorereviews_processed.csv'), index=False)
real_install.to_csv(os.path.join(data_processed_dir, 'real_install_processed.csv'), index=False)

# Convert the date columns to datetime
tickvah_ads['date'] = pd.to_datetime(tickvah_ads['date'])
App_install['date'] = pd.to_datetime(App_install['date'])
telegramsubscription['date'] = pd.to_datetime(telegramsubscription['date'])
playstorereviews['at'] = pd.to_datetime(playstorereviews['at'])

# Aggregate the sentiment data to a daily level
daily_sentiment = playstorereviews.groupby([playstorereviews['at'].dt.date, 'sentiment']).size().unstack(fill_value=0)

# Reset the index and rename the columns
daily_sentiment.index = pd.to_datetime(daily_sentiment.index)
daily_sentiment = daily_sentiment.rename_axis('date').reset_index()

# Merge all DataFrames on the 'date' column
merged_df = pd.merge(tickvah_ads, App_install, on='date', how='outer')
merged_df = pd.merge(merged_df, telegramsubscription, on='date', how='outer')
merged_df = pd.merge(merged_df, daily_sentiment, on='date', how='outer')

# Fill missing values with 0 for sentiment columns
sentiment_cols = ['positive', 'negative', 'neutral']
for col in sentiment_cols:
    if col not in merged_df:
        merged_df[col] = 0

merged_df[sentiment_cols] = merged_df[sentiment_cols].fillna(0)

# Visualization

# Plot install count over time
plt.figure(figsize=(14, 7))
sns.lineplot(data=merged_df, x='date', y='install_count', label='Install Count')
plt.title('Daily Install Count Over Time')
plt.xlabel('Date')
plt.ylabel('Install Count')
plt.legend()
plt.show()

# Plot subscriber count over time
plt.figure(figsize=(14, 7))
sns.lineplot(data=merged_df, x='date', y='subscribers', label='Subscribers')
plt.title('Subscribers Over Time')
plt.xlabel('Date')
plt.ylabel('Subscribers')
plt.legend()
plt.show()

# Plot sentiment over time
plt.figure(figsize=(14, 7))
sns.lineplot(data=merged_df, x='date', y='positive', label='Positive Sentiment')
sns.lineplot(data=merged_df, x='date', y='negative', label='Negative Sentiment')
sns.lineplot(data=merged_df, x='date', y='neutral', label='Neutral Sentiment')
plt.title('Daily Sentiment Over Time')
plt.xlabel('Date')
plt.ylabel('Sentiment Count')
plt.legend()
plt.show()

# Correlation Analysis

# Calculate the correlation matrix
correlation_matrix = merged_df[['install_count', 'subscribers'] + sentiment_cols].corr()

# Plot the correlation matrix
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title('Correlation Matrix')
plt.show()

# Time Series Decomposition for Install Count
decomposition = seasonal_decompose(merged_df.set_index('date')['install_count'].fillna(0), model='additive', period=30)

plt.figure(figsize=(14, 10))
plt.subplot(411)
plt.plot(decomposition.observed, label='Observed')
plt.legend(loc='upper left')
plt.subplot(412)
plt.plot(decomposition.trend, label='Trend')
plt.legend(loc='upper left')
plt.subplot(413)
plt.plot(decomposition.seasonal, label='Seasonal')
plt.legend(loc='upper left')
plt.subplot(414)
plt.plot(decomposition.resid, label='Residual')
plt.legend(loc='upper left')
plt.tight_layout()
plt.show()
