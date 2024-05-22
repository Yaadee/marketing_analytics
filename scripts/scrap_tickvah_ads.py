import logging
import asyncio
import csv
from datetime import datetime, timezone
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import InputMessagesFilterEmpty

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram API credentials
api_id = '26622716'
api_hash = 'fd4274717bfcacf787cc15b9b51f1c76'
tikvah_channel_username = 'tikvahethiopia'
banks_channel_username = 'BoAEth'  

# Function to scrape bank advertisements from Telegram channel
async def scrape_telegram_channel(client, channel_username, start_date, end_date):
    ads = []
    try:
        channel_entity = await client.get_entity(channel_username)
        logger.info(f"Successfully retrieved channel entity for {channel_username}")
        async for message in client.iter_messages(channel_entity, filter=InputMessagesFilterEmpty):
            logger.info(f"Checking message ID: {message.id} with date: {message.date}")
            if message.date < start_date:
                logger.info("Reached messages older than start_date, stopping.")
                break
            if start_date <= message.date <= end_date:
                logger.info(f"Processing message ID: {message.id}")
                if message.text and any(keyword in message.text for keyword in ["#BankofAbyssinia", "#አቢሲንያ_ባንክ"]):
                    ad_info = {
                        'date': message.date.strftime("%Y-%m-%d %H:%M:%S"),
                        'post_link': f"https://t.me/{channel_username}/{message.id}",
                        'view': message.views,
                        'post_hour': message.date.hour,
                        'bank': 'BOA',
                        'time_of_day': (
                            "Morning" if 6 <= message.date.hour < 12 else 
                            "Afternoon" if 12 <= message.date.hour < 18 else 
                            "Evening"
                        )
                    }
                    ads.append(ad_info)
                    logger.info(f"Ad found: {ad_info}")
                else:
                    logger.info(f"Message ID {message.id} did not match keywords.")
    except Exception as e:
        logger.error(f"Error occurred while scraping Telegram channel: {e}")
    return ads

# Function to save ads data to CSV file
def save_ads_to_csv(data, filename):
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['date', 'post_link', 'view', 'post_hour', 'bank', 'time_of_day']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for ad in data:
                writer.writerow(ad)
        logger.info(f"Successfully saved {len(data)} records to {filename}.")
    except Exception as e:
        logger.error(f"Error occurred while saving data to CSV: {e}")

async def main():
    start_date = datetime(2017, 1, 1, tzinfo=timezone.utc)
    end_date = datetime.now(timezone.utc)
    
    async with TelegramClient('session_name', api_id, api_hash) as client:
        # Scrape ads data
        ads_data = await scrape_telegram_channel(client, tikvah_channel_username, start_date, end_date)
        if ads_data:
            save_ads_to_csv(ads_data, 'data/raw/bank_ads.csv')
        else:
            logger.info("No ads found in the specified date range.")

if __name__ == '__main__':
    asyncio.run(main())
