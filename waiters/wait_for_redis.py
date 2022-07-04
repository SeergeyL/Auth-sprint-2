import os

import redis

from backoff import backoff


@backoff()
def wait_for_redis():
    host = os.environ.get('REDIS_HOST')
    port = os.environ.get('REDIS_PORT')
    redis_client = redis.Redis(
        host=host,
        port=port
    )
    redis_client.ping()


wait_for_redis()
