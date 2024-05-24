from sqlalchemy import create_engine, text

def get_database_engine(db_name, db_user, db_password, db_host, db_port):
    # Create the database connection URL
    db_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    # Create the database engine
    engine = create_engine(db_url)
    return engine

def insert_subscription_data(conn, data, table_name):
    try:
        data.to_sql(table_name, conn, if_exists='append', index=False)
        print(f"Data inserted successfully into the PostgreSQL table {table_name}")
    except Exception as e:
        print(f"Error occurred while inserting data into PostgreSQL: {e}")

def close_connection(conn):
    try:
        conn.close()
        print("Connection to the PostgreSQL database closed.")
    except Exception as e:
        print(f"Error occurred while closing connection to PostgreSQL database: {e}")
