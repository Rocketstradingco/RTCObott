import json
from pathlib import Path
import logging

DATA_FILE = Path('data/inventory.json')
logger = logging.getLogger(__name__)


DEFAULT_DATA = {
    "categories": [],
    "embed": {
        "title": "",
        "description": "",
        "button_label": "Explore",
        "color": "#ffffff",
        "thumbnail": "",
        "image": "",
        "footer": "",
    },
    "settings": {
        "inventory_channel_id": "",
        "claims_channel_id": "",
        "image_channel_id": "",
        "grid_size": 3,
        "claims_message_id": "",
    },
}


def load_data():
    """Load inventory and embed configuration."""
    logger.debug('Loading data from %s', DATA_FILE)
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE) as f:
                data = json.load(f)
        except json.JSONDecodeError:
            logger.error('Corrupted JSON in %s, backing up and resetting', DATA_FILE)
            backup = DATA_FILE.with_suffix(DATA_FILE.suffix + '.bak')
            DATA_FILE.rename(backup)
            logger.info('Moved bad file to %s', backup)
            data = DEFAULT_DATA.copy()
        for k, v in DEFAULT_DATA.items():
            if isinstance(v, dict):
                data.setdefault(k, {})
                for sk, sv in v.items():
                    data[k].setdefault(sk, sv)
            else:
                data.setdefault(k, v)
        return data
    return DEFAULT_DATA.copy()


def save_data(data):
    logger.debug('Saving data to %s', DATA_FILE)
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
