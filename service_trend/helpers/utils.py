import os
from dotenv import load_dotenv
import logging

load_dotenv()

def get_env(key, default=None):
    return os.getenv(key, default)

def setup_logger():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    return logging.getLogger("analyzes")
