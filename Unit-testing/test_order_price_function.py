import pytest
import pandas as pd
import logging
from lambda_function_testing import order_price_cleaning, remove_sensitive_data


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

df = pd.read_csv('chesterfield_25-08-2021_09-00-00.csv')
df.columns = ['DateTime', 'Location', 'Name', '_', 'Order_Total_Amount', 'PaymentMethod', '_']


def test_exception_order_price_cleaning():
    with pytest.raises(Exception):
        order_price_cleaning(df)


def test_remove_sensitive_data():
    with pytest.raises(Exception):
        remove_sensitive_data(df)
