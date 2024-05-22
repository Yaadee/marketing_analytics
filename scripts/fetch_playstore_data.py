import pandas as pd
from sqlalchemy import create_engine

# Read the CSV file into a DataFrame
df = pd.read_csv('/home/yadasa/Desktop/marketing-analytics/data/raw/bank_ads.csv')

# Establish a connection to the PostgreSQL database
engine = create_engine('postgresql://postgres:admin@localhost:5432/tickvah_banks_ads')
df.head()

# Create a table in the database (if it doesn't exist)
# Replace 'table_name' and specify column data types according to your DataFrame
df.to_sql('bank_advertisements', engine, if_exists='replace', index=False)