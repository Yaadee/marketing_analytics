import asyncio
import os
import pandas as pd
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from db_connection import get_database_engine, close_connection

# Function to save data to a CSV file
def save_to_csv(data, filename):
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)  # Ensure directory exists
        if os.path.exists(filename):
            data.to_csv(filename, mode='a', header=False, index=False)  # Append to existing file without writing the header again
        else:
            data.to_csv(filename, index=False)
        print(f"Successfully saved data to {filename}")
    except Exception as e:
        print(f"Error occurred while saving data to CSV file: {e}")

# Function to fetch channel info
async def get_channel_info(api_id, api_hash, channel_username, date):
    try:
        async with TelegramClient('session_name', api_id, api_hash) as client:
            await client.start()
            channel = await client.get_entity(channel_username)
            full_channel = await client(GetFullChannelRequest(channel=channel))
            channel_info = {
                'date': date,
                'subscribers': full_channel.full_chat.participants_count
            }
            return channel_info
    except Exception as e:
        print(f"Error fetching channel info: {e}")
        return None

# Function to insert data into PostgreSQL
def insert_subscription_data(engine, data, table_name):
    try:
        data.to_sql(table_name, engine, if_exists='append', index=False)
        print(f"Data inserted successfully into the PostgreSQL table {table_name}")
    except Exception as e:
        print(f"Error occurred while inserting data into PostgreSQL: {e}")

# Main function to fetch daily subscription data
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
    engine = get_database_engine(db_name, db_user, db_password, db_host, db_port)
    
    # Define the starting date and date range for data collection
    start_date = datetime(2017, 1, 1)
    end_date = datetime.now()
    
    # Fetch daily subscription data
    current_date = start_date
    daily_data = []
    while current_date <= end_date:
        channel_info = await get_channel_info(api_id, api_hash, channel_username, current_date)
        if channel_info:
            daily_data.append(channel_info)
        current_date += timedelta(days=1)
        
    # Convert to DataFrame and save daily data to CSV and database
    if daily_data:
        daily_df = pd.DataFrame(daily_data)
        save_to_csv(daily_df, 'data/raw/telegram_channel_info.csv')
        insert_subscription_data(engine, daily_df, 'telegram_channel_info.csv')
    
    # Close database connection
    close_connection(engine)

if __name__ == "__main__":
    asyncio.run(main())
