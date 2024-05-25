import pandas as pd
from sqlalchemy import create_engine

def get_database_engine(db_name, db_user, db_password, db_host, db_port):
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    return engine

def close_connection(engine):
    engine.dispose()

def insert_data_to_postgres(engine, data, table_name):
    try:
        data.to_sql(table_name, engine, if_exists='append', index=False)
        print(f"Data inserted successfully into the PostgreSQL table {table_name}")
    except Exception as e:
        print(f"Error occurred while inserting data into PostgreSQL: {e}")

def migrate_csv_to_postgres(csv_file_path, table_name, database_url):
    df = pd.read_csv(csv_file_path)
    engine = create_engine(database_url)
    insert_data_to_postgres(engine, df, table_name)
    close_connection(engine)

# Database credentials
db_name = 'tickvah_banks_ads'
db_user = 'postgres'
db_password = 'admin'
db_host = 'localhost'
db_port = '5432'
database_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

# Migrate CSV files to PostgreSQL with corresponding table names
csv_files = [
    ('daily_telegram_subscriptions.csv', 'telegram_subscriptions'),
    ('playstore_reviews.csv', 'playstore_reviews_info'),
    ('bank_ads.csv', 'bank_advertisements'),
    ('installations.csv', 'real_install_count')
]

for csv_file, table_name in csv_files:
    csv_file_path = f'data/raw/{csv_file}'
    migrate_csv_to_postgres(csv_file_path, table_name, database_url)
