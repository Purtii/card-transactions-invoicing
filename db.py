
import os
import sys

import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_connection() -> psycopg.Connection:
    url = os.getenv("DATABASE_URL")
    if not url or "[YOUR-PASSWORD]" in url:
        sys.exit("Lipsește DATABASE_URL din fișierul .env (sau mai conține [YOUR-PASSWORD]).")
    return psycopg.connect(url)
