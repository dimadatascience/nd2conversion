import logging
import os

def setup_logging():
    logging.basicConfig(level=logging.DEBUG, filemode='a+', format='%(asctime)s - %(levelname)s - %(message)s')