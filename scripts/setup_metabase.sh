#!/bin/bash

# Ensure you have Python installed and the necessary dependencies

# Execute db_connection.py
python db_connection.py

# Execute scrap_tickvah_ads.py
python scrap_tickvah_ads.py

# Execute fetch_playstore_data.py
python fetch_playstore_data.py

# Execute fetch_telegram_data.py
python fetch_telegram_data.py

# Execute migrate_database.py
python migrate_database.py

# Execute process_data.py (analysis and visualization)
python process_data.py
