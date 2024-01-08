import json
import csv
import logging
import pandas as pd
import boto3
import hashlib
import psycopg2
import os


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

#=============================================================================================================================================
#                                                              Setting up database connection
#=============================================================================================================================================

# Get the SSM Param from AWS and turn it into JSON
# Don't log the password!
ssm_client = boto3.client('ssm')

def get_ssm_param(param_name):
    print(f'get_ssm_param: getting param_name={param_name}')
    parameter_details = ssm_client.get_parameter(Name=param_name)
    redshift_details = json.loads(parameter_details['Parameter']['Value'])

    host = 'redshiftcluster-h0ppssmszukx.cyedtoskxrzl.eu-west-1.redshift.amazonaws.com'
    user = redshift_details['user']
    password = redshift_details['password']
    db = redshift_details['database-name']

    print(f'get_ssm_param loaded for db={db}, user={user}, host={host}')

    return host, user, password, db

# Connecting to the database using parameters from SSM
def open_database_connection():
    try:
         # Get Redshift details from SSM
        rs_host, rs_user, rs_password, rs_dbname = get_ssm_param('marios_espresso_pipeline_redshift_settings')  # Fix here

        # Establish connection using psycopg2
        connection = psycopg2.connect(
            host=rs_host,
            port=5439,
            user=rs_user,
            password=rs_password,
            database=rs_dbname
        )
        cursor = connection.cursor()
        print('Connected to the database.')
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
            print('Connection closed.')
    except Exception as ex:
        print('Failed to close connection:', ex)



#=============================================================================================================================================
#                                                              Extracting and transforming data
#=============================================================================================================================================

s3 = boto3.client('s3')
def read_csv_from_s3(bucket, key):
    try:
        LOGGER.info(f'Reading CSV from S3: bucket={bucket}, key={key}')
        obj = s3.get_object(Bucket=bucket, Key=key)
        df = pd.read_csv(obj['Body'])
        df.columns = ['DateTime', 'Location', 'Name', 'Order', 'Order_Total_Amount', 'PaymentMethod', 'CardNumber']
        pd.set_option('display.max_rows', None)
        return df
    except Exception as e:
        LOGGER.error(f'Error reading CSV from S3: {e}')
        raise

def order_price_cleaning(df):
    try:
        LOGGER.info('Cleaning order price data')
        df['Order'] = df['Order'].str.split(",")
        df = df.explode('Order')
        df[['Product', 'Price']] = df['Order'].str.rsplit('-', n=1, expand=True)
        df[['Product_Name', 'Flavour']] = df['Product'].str.rsplit('-', n=1, expand=True)
        df[['Size', 'Product_Type']] = df['Product_Name'].str.split(n=1, expand=True)

        ### DROP ORDER, PRODUCT AND PRODUCT_NAME COLUMNS ###
        df.drop(columns=['Product_Name', 'Product', 'Order'], axis=1, inplace=True)

        LOGGER.info(f'DataFrame Shape After: {df.shape}, Columns After: {df.columns}')

        return df
    except Exception as e:
        LOGGER.error(f'Error in order price cleaning: {e}')
        raise

def generate_pseudo_random_id(data):
    # Add your pseudo-random ID generation logic here
    return hashlib.sha256(data.encode()).hexdigest()

def process_dataframe(df):
    try:
        LOGGER.info('Processing DataFrame')

        # Perform order price cleaning
        df = order_price_cleaning(df)

        # Convert 'DateTime' column to the required format
        df['DateTime'] = pd.to_datetime(df['DateTime'], format='%d/%m/%Y %H:%M').dt.strftime('%Y-%m-%d %H:%M:%S')


        # Using hashing
        df['Product_id'] = df.apply(lambda row: generate_pseudo_random_id(str(row['Flavour']) + str(row['Size']) + str(row['Product_Type']) + str(row['Price'])), axis=1)
        df['Customer_id'] = df['Name'].apply(lambda _: generate_pseudo_random_id(_))
        df['Order_id'] = df.apply(lambda row: generate_pseudo_random_id(str(row['DateTime']) + str(row['Location']) + str(row['Name'])), axis=1)
        df['Branch_id'] = df.apply(lambda row: generate_pseudo_random_id(str(row['Location']) + str(row['DateTime'])), axis=1)

        # Drop unnecessary columns after processing
        df.drop(columns=['Name', 'CardNumber'], axis=1, inplace=True)

        LOGGER.info(f'DataFrame Shape After: {df.shape}, Columns After: {df.columns}')

        LOGGER.info('Processing completed successfully!')
        return df
    except Exception as e:
        LOGGER.error(f'Error in process_dataframe: {e}')
        raise



#=============================================================================================================================================
#                                                                   Loading data to Redshift
#=============================================================================================================================================

def load_data_into_redshift_branches_table(connection, cursor, df):
    for index, row in df.iterrows():
        # iterate through each row in df
        branch_id = row['Branch_id']
        branch_location = row['Location']
        # insert into table
        sql = "INSERT INTO branches (branch_id, branch_location) VALUES (%s, %s)"
        new_data_values = (branch_id, branch_location)
        cursor.execute(sql, new_data_values)
    connection.commit()


def load_data_into_redshift_orders_table(connection, cursor, df):
    # iterate through each row in df
    for index, row in df.iterrows():
        order_id = row['Order_id']
        order_timestamp = row['DateTime']
        customer_id = row['Customer_id']
        branch_id = row['Branch_id']
        total_spend = row['Order_Total_Amount']
        payment_method = row['PaymentMethod']
        # insert into table
        sql = "INSERT INTO orders (order_id, order_timestamp, branch_id, customer_id, total_spend, payment_method) VALUES (%s, %s, %s, %s, %s, %s)"
        new_data_values = (order_id, order_timestamp, branch_id, customer_id, total_spend, payment_method)
        cursor.execute(sql, new_data_values)
    connection.commit()


def load_data_into_redshift_products_table(connection, cursor, df):
    # iterate through each row in df
    for index, row in df.iterrows():
        product_id = row['Product_id']
        product_name = row['Product_Type']
        product_flavour = row['Flavour']
        product_size = row['Size']
        price = row['Price']
        # insert into table
        sql = "INSERT INTO products (product_id, product_name, product_flavour, product_size, price) VALUES (%s, %s, %s, %s, %s)"
        new_data_values = (product_id, product_name, product_flavour, product_size, price)
        cursor.execute(sql, new_data_values)
    connection.commit()

def load_data_into_redshift_orders_details_table(connection, cursor, df):
    for index, row in df.iterrows():
        order_id = row['Order_id']
        product_id = row['Product_id']
        # insert into table
        sql = "INSERT INTO orders_details (order_id, product_id) VALUES (%s, %s)"
        new_data_values = (order_id, product_id)
        cursor.execute(sql, new_data_values)
    connection.commit()


#=============================================================================================================================================
#                                                                  Event handler
#=============================================================================================================================================
def handler(event, context):
    try:
        LOGGER.info(f'Event structure: {event}')

        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

        LOGGER.info(f'Received S3 event: bucket={bucket}, key={key}')

        df = read_csv_from_s3(bucket, key)
        processed_df = process_dataframe(df)

        LOGGER.info(f'Processed DataFrame Shape: {processed_df.shape}, Columns: {processed_df.columns}')

        # Connect to the database
        connection, cursor = open_database_connection()


        try:
            load_data_into_redshift_orders_table(connection, cursor, processed_df)
        except Exception as e:
            LOGGER.error(f"Error loading 'orders' data into Redshift: {e}")
            raise


        #close database connection
        close_database_connection(connection, cursor)

        # process complete
        return {
            'statusCode': 200,
            'body': json.dumps('Processing completed successfully!')
        }

    except Exception as e:
        LOGGER.error(f'Error in handler function: {e}')
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error in handler function: {e}')
        }