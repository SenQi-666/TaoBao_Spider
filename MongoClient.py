import pymongo
from conf.Settings import *


class Mongo:
    def __init__(self):
        self.Client = pymongo.MongoClient('mongodb://%s:%s@%s:%s/' % (MongoUSER, MongoPWD, MongoHOST, MongoPORT))
        self.Collection = self.Client[MongoDB][MongoColl]
