import os

import redis
redisCon=None
def connect():
    global redisCon
    if redisCon is None:
        host = os.getenv("REDIS_HOST").split(":")
        redisCon = redis.StrictRedis(host=host[0], port=int(host[1]))

    return redisCon