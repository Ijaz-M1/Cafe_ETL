import pandas as pd
import logging


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

def order_price_cleaning(df):
    try:
        df['Order'] = df['Order'].str.split(",")
        df = df.explode('Order')
        df[['Product', 'Price']] = df['Order'].str.rsplit('-', n=1, expand=True)


        df[['Product_Name', 'Flavour']] = df['Product'].str.rsplit('-', n=1, expand=True)

        print("DataFrame Shape After:", df.shape)
        print("Columns After:", df.columns)

        df[['Size','Product']] = df['Product'].str.split(n=1, expand=True)
        return df
    except Exception as e:
        LOGGER.error(f'Error in order price cleaning: {e}')
        raise


def remove_sensitive_data(df):
    df.drop(columns=['Name', 'CardNumber'], axis=1, inplace=True)