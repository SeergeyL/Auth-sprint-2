import abc
import redis
from flask import Flask


class AbstractCache(abc.ABC):
    @abc.abstractmethod
    def get(self):
        pass

    def set(self):
        pass


class RedisCache(AbstractCache):
    def __init__(self):
        self.redis = None
    
    def init_app(self, app: Flask):
        self.redis = redis.Redis(
            host=app.config['REDIS_HOST'],
            port=app.config['REDIS_PORT'],
            db=0
        )

    def set(self, *args, **kwargs):
        self.redis.set(*args, **kwargs)
    
    def get(self, *args, **kwargs):
        return self.redis.get(*args, **kwargs)


redis_db = RedisCache()

def init_cache(app: Flask):
    redis_db.init_app(app)
