from cassandra.cluster import Cluster

class cassandraDb:
    def __init__(self, ips):
        self.cluster = Cluster(ips)
        self.session =  self.cluster.connect()

    def keyspaceCreation(self):
        keyspaceCreation = "CREATE KEYSPACE urls WITH replication = {'class': 'SimpleStrategy', 'replication_factor' : 2};"
        self.session.execute(keyspaceCreation)

    def tableCreation(self):
        tableCreation = "CREATE TABLE urls (shorten TEXT PRIMARY KEY, long TEXT);"
        self.session.execute(tableCreation)

    def setKeyspace(self):
        self.session.set_keyspace('urls')

    def insertUrl(self, short, long):
        preparedInsertStatement = "INSERT INTO urls (shorten, long) VALUES (?,?)"
        prep = self.session.prepare(preparedInsertStatement)
        self.session.execute(prep, (short, long))

    def selectUrl(self, short):
        preparedSelectStatement = "SELECT * FROM urls WHERE shorten = (?)"
        prep = self.session.prepare(preparedSelectStatement)
        result = self.session.execute(prep, (short,))
        return result
