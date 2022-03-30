import os
import json
from pathlib import Path
from dotenv import load_dotenv

from distutils.util import strtobool

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / '.env', override=False)

# region DB config
_DB_HOST = os.environ.get('DB_HOST', 'db')
_DB_PORT = os.environ.get('DB_PORT', "5432")
_DB_NAME = os.environ.get('POSTGRES_DB', "offers_collector")
_DB_USER = os.environ.get('POSTGRES_USER', 'collector')
_DB_PASSWORD = os.environ['POSTGRES_PASSWORD']

DB_URI = f'postgresql://{_DB_USER}:{_DB_PASSWORD}@{_DB_HOST}:{_DB_PORT}/{_DB_NAME}'
DB_CONFIG = {
    'default': 'postgres',
    'postgres': {
        'driver': 'psycopg',
        'host': _DB_HOST,
        'database': _DB_NAME,
        'user': _DB_USER,
        'password': _DB_PASSWORD,
        'prefix': ''
    }
}
SQLALCHEMY_BINDS = {'default': DB_URI}

# endregion

IS_DEBUG = bool(strtobool(os.environ.get('IS_DEBUG', 'False')))

# region AUTH
ACCOUNT_EMAIL = os.environ['ACCOUNT_EMAIL']
API_KEY_ID = os.environ['API_KEY_ID']
with open(BASE_DIR / '.api_key.json') as file:
    API_KEY = json.load(file)
# endregion

