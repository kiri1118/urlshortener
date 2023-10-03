from redis import Redis, RedisError
from ast import literal_eval

class redisMaster:
    def __init__(self, db=0):
        self.redis = Redis(host='redis-master', db=db)

    def get(self, key):
        return (self.redis.get(key)).decode()

    def set(self, key, value):
        self.redis.set(key, value)
    
    def addToQueue(self, value):
        self.redis.rpush('cassandraQueue', str(value))

    def getNextInQueue(self):
        return literal_eval(self.redis.blpop(['cassandraQueue'])[1].decode())

    def isQueueEmpty(self):
        return self.redis.llen('cassandraQueue') == 0
    
    def startExpireCountdown(self, key):
        self.redis.expire(key, 60)

class redisSlave:
    def __init__(self, db=0):
        self.redis = Redis(host='redis-slave', db=db, socket_connect_timeout=2, socket_timeout=2)
        print(self.redis)

    def get(self, key):
        value = self.redis.get(key)
        if (value is not None):
            return (self.redis.get(key)).decode()
        else:
            return None

    def getKeys(self):
        return self.redis.keys("*")
