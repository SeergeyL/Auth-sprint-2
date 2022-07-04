import os

import psycopg2

from backoff import backoff


@backoff()
def wait_for_db():
    dsn = {
        'host': os.environ.get('POSTGRES_HOST'),
        'port': os.environ.get('POSTGRES_PORT'),
        'user': os.environ.get('POSTGRES_USER'),
        'password': os.environ.get('POSTGRES_PASSWORD'),
        'dbname': os.environ.get('POSTGRES_DATABASE')
    }
    psycopg2.connect(**dsn)
    

wait_for_db()
