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