import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()
host_name = os.environ.get("postgres_host")
database_name = os.environ.get("postgres_db")
user_name = os.environ.get("postgres_user")
user_password = os.environ.get("postgres_pass")

def open_database_connection():
    try:
        connection = psycopg2.connect(
            database = "test",
            user = "root",
            host= 'localhost',
            password = "password"
        )
        cursor = connection.cursor()
        return connection, cursor
    except Exception as ex:
        print('Failed to open connection:', ex)
        return None, None

def close_database_connection(connection, cursor):
    try:
        print('Closing cursor...')
        if cursor:
            cursor.close()
        if connection:
            print('Closing connection...')
            connection.close()
    except Exception as ex:
        print('Failed to close connection:', ex)

if __name__ == "__main__":
    connection, cursor = open_database_connection()
