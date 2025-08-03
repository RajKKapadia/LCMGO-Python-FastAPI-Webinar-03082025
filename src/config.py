import os
import uuid

from dotenv import load_dotenv, find_dotenv
import redis

load_dotenv(find_dotenv())

DATABASE_URL = os.getenv("DATABASE_URL")

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

SESSION_EXPIRATION_TIME = 1440


def generate_uuid():
    """
    Generate a unique UUID for database records
    """
    return str(uuid.uuid4())
