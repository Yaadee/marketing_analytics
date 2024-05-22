# db_connection.py
from sqlalchemy import create_engine, text

def get_database_engine(db_name, db_user, db_password, db_host, db_port):
    # Create the database connection URL
    db_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    # Create the database engine
    engine = create_engine(db_url)
    return engine

def insert_ads_data(conn, ads_data):
    try:
        for ad in ads_data:
            conn.execute(text("""
                INSERT INTO bank_advertisements (date, post_link, view, post_hour)
                VALUES (:date, :post_link, :view, :post_hour)
            """), ad)
        conn.commit()
        print("Successfully inserted data into PostgreSQL database.")
    except Exception as e:
        print(f"Error occurred while inserting data into PostgreSQL database: {e}")

def close_connection(conn):
    try:
        conn.close()
        print("Connection to the PostgreSQL database closed.")
    except Exception as e:
        print(f"Error occurred while closing connection to PostgreSQL database: {e}")