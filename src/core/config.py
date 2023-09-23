import os
from logging import config as logging_config

from dotenv import load_dotenv

from src.core.logger import LOGGING

logging_config.dictConfig(LOGGING)
load_dotenv()

PROJECT_NAME = os.getenv('PROJECT_NAME', 'dining room')
PROJECT_HOST = os.getenv('PROJECT_HOST', '127.0.0.1')
PROJECT_PORT = int(os.getenv('PROJECT_PORT', '8080'))

DSN = os.getenv(
    'DSN', 'sqlite+aiosqlite:///dining_room.db'
)
