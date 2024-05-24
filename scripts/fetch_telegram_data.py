# import os
# import pandas as pd
# import logging
# import asyncio
# from datetime import datetime, timedelta
# from sqlalchemy import create_engine
# from telethon import TelegramClient
# from telethon.tl.functions.channels import GetFullChannelRequest
# from db_connection import get_database_engine, close_connection

# # Configure logging
# logging.basicConfig(filename='scraping.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

# # Function to save data to a CSV file
# def save_to_csv(data, filename):
#     try:
#         os.makedirs(os.path.dirname(filename), exist_ok=True)  # Ensure directory exists
#         if os.path.exists(filename):
#             data.to_csv(filename, mode='a', header=False, index=False)  # Append to existing file without writing the header again
#         else:
#             data.to_csv(filename, index=False)
#         logging.info(f"Successfully saved data to {filename}")
#     except Exception as e:
#         logging.error(f"Error occurred while saving data to CSV file: {e}")

# # Function to fetch daily subscription count
# async def get_daily_subscription_count(api_id, api_hash, channel_username, date):
#     try:
#         async with TelegramClient('session_name', api_id, api_hash) as client:
#             await client.start()
#             channel = await client.get_entity(channel_username)
#             full_channel = await client(GetFullChannelRequest(channel=channel))
#             subscribers = full_channel.full_chat.participants_count
#             logging.info(f"Fetched daily subscription count for {date}: {subscribers}")
#             return {'date': date, 'subscribers': subscribers}
#     except Exception as e:
#         logging.error(f"Error fetching daily subscription count for {date}: {e}")
#         return None

# # Function to insert data into PostgreSQL
# def insert_subscription_data(engine, data, table_name):
#     try:
#         data.to_sql(table_name, engine, if_exists='append', index=False)
#         logging.info(f"Data inserted successfully into the PostgreSQL table {table_name}")
#     except Exception as e:
#         logging.error(f"Error occurred while inserting data into PostgreSQL: {e}")

# # Main function to fetch daily subscription count
# async def main():
#     # Your Telegram API credentials
#     api_id = '26622716'
#     api_hash = 'fd4274717bfcacf787cc15b9b51f1c76'
#     channel_username = 'BoAEth'
    
#     # Database credentials
#     db_name = 'tickvah_banks_ads'
#     db_user = 'postgres'
#     db_password = 'admin'
#     db_host = 'localhost'
#     db_port = '5432'
    
#     # Connect to the database
#     engine = get_database_engine(db_name, db_user, db_password, db_host, db_port)
    
#     # Define the starting date and date range for data collection
#     start_date = datetime(2017, 1, 1)
#     end_date = datetime.now()
    
#     # Fetch daily subscription data
#     current_date = start_date
#     daily_data = []
#     while current_date <= end_date:
#         daily_subscription_count = await get_daily_subscription_count(api_id, api_hash, channel_username, current_date)
#         if daily_subscription_count:
#             daily_data.append(daily_subscription_count)
#         current_date += timedelta(days=1)
#     print(daily_subscription_count)
#     # Convert to DataFrame and save daily data to CSV and database
#     if daily_data:
#         daily_df = pd.DataFrame(daily_data)
#         save_to_csv(daily_df, 'data/raw/daily_telegram_subscriptions.csv')
#         insert_subscription_data(engine, daily_df, 'daily_telegram_subscriptions')
    
#     # Close database connection
#     close_connection(engine)

# if __name__ == "__main__":
#     asyncio.run(main())
import os
import pandas as pd
import logging
import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from db_connection import*

# Configure logging
logging.basicConfig(filename='scraping.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

# Function to save data to a CSV file
def save_to_csv(data, filename):
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)  # Ensure directory exists
        if os.path.exists(filename):
            data.to_csv(filename, mode='a', header=False, index=False)  # Append to existing file without writing the header again
        else:
            data.to_csv(filename, index=False)
        logging.info(f"Successfully saved data to {filename}")
    except Exception as e:
        logging.error(f"Error occurred while saving data to CSV file: {e}")

# Function to fetch daily subscription count
async def get_daily_subscription_count(api_id, api_hash, channel_username, date):
    try:
        async with TelegramClient('session_name', api_id, api_hash) as client:
            await client.start()
            channel = await client.get_entity(channel_username)
            full_channel = await client(GetFullChannelRequest(channel=channel))
            subscribers = full_channel.full_chat.participants_count
            logging.info(f"Fetched daily subscription count for {date}: {subscribers}")
            return {'date': date, 'subscribers': subscribers}
    except Exception as e:
        logging.error(f"Error fetching daily subscription count for {date}: {e}")
        return None

# Main function to fetch daily subscription count
async def main():
    # Your Telegram API credentials
    api_id = '26622716'
    api_hash = 'fd4274717bfcacf787cc15b9b51f1c76'
    channel_username = 'BoAEth'
    
    # Database credentials
    db_name = 'tickvah_banks_ads'
    db_user = 'postgres'
    db_password = 'admin'
    db_host = 'localhost'
    db_port = '5432'
    
    # Connect to the database
    db_engine = get_database_engine(db_name, db_user, db_password, db_host, db_port)
    
    # Define the starting date as today
    start_date = datetime.now()
    end_date = start_date  # End date is also today
    
    # Fetch daily subscription data
    current_date = start_date
    daily_data = []
    while current_date <= end_date:
        daily_subscription_count = await get_daily_subscription_count(api_id, api_hash, channel_username, current_date)
        if daily_subscription_count:
            daily_data.append(daily_subscription_count)
        current_date += timedelta(days=1)
    
    # Convert to DataFrame and save daily data to CSV and database
    if daily_data:
        daily_df = pd.DataFrame(daily_data)
        save_to_csv(daily_df, 'data/raw/daily_telegram_subscriptions.csv')
        insert_subscription_data(db_engine, daily_df, 'daily_telegram_subscriptions')
    
    # Close database connection
    close_connection(db_engine)

if __name__ == "__main__":
    asyncio.run(main())


