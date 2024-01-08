import pandas as pd
import csv
import pytest


def test_extraction():
    file_path ='team-3-project\chesterfield_25-08-2021_09-00-00.csv'
    df = pd.read_csv(file_path, header=None, names=['DateTime', 'Location', 'Name', 'Order', 'Order_Total_Amount', 'PaymentMethod', 'CardNumber'])
    df['Order_Total_Amount'] = df['Order_Total_Amount'].astype(str)
    df['CardNumber'] = df['CardNumber'].astype(str)
    result = df.iloc[0]
    return result

expected = {
    'DateTime': '25/08/2021 09:00',
    'Location': 'Chesterfield',
    'Name': 'Richard Copeland',
    'Order': 'Regular Flavoured iced latte - Hazelnut - 2.75, Large Latte - 2.45',
    'Order_Total_Amount': '5.2',
    'PaymentMethod': 'CARD',
    'CardNumber': '5490000000000000.0'
}

# Call the function and assign the result to a variable
result = test_extraction()
result.name = None

# Convert the expected dictionary to a pandas series
expected = pd.Series(expected)


# Compare the result and the expected series using the assert_series_equal function
# Remove the assert statement
pd.testing.assert_series_equal(result, expected)