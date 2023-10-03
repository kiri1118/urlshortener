from redisDb import redisMaster, redisSlave
from redis import Redis
from cassandraDb import cassandraDb
import time

redisMaster = redisMaster()
db = cassandraDb(['10.11.1.118', '10.11.2.118', '10.11.3.118']) # CHANGE THIS IP WHEN RUNNING
try:
    db.keyspaceCreation()
except:
    pass
db.setKeyspace()
try:
    db.tableCreation()
except:
    pass

while True:
    if redisMaster.isQueueEmpty():
        # Queue is empty, so put process to sleep
        time.sleep(30)
    else:
        addingToCassandra = redisMaster.getNextInQueue()
        for key in addingToCassandra:
            db.insertUrl(key, addingToCassandra[key]) # add to cassandra
            redisMaster.startExpireCountdown(key) # start counting for TTL for key after its added to cassandra
