import json
from pathlib import Path
import logging

DATA_FILE = Path('data/inventory.json')
logger = logging.getLogger(__name__)


def load_data():
    logger.debug('Loading data from %s', DATA_FILE)
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"categories": []}


def save_data(data):
    logger.debug('Saving data to %s', DATA_FILE)
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
