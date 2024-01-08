import hashlib
import logging

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

def generate_pseudo_random_id(data):
    try:
        return hashlib.sha256(data.encode()).hexdigest()
    except Exception as e:
        LOGGER.error(f'Error in order price cleaning: {e}')
        raise


def test_generate_pseudo_random_id():
    # Test with valid input
    data = "testing_the_data"
    expected_output = hashlib.sha256(data.encode()).hexdigest()
    assert generate_pseudo_random_id(data) == expected_output


def test_generate_pseudo_random_id_empty():
    # Test with empty string
    empty_data = ""
    expected_output_empty = hashlib.sha256(empty_data.encode()).hexdigest()
    assert generate_pseudo_random_id(empty_data) == expected_output_empty