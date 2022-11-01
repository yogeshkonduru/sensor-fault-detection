import pymongo
from sensor.constant.database import DATABASE_NAME
from sensor.constant.env_variable import MONGODB_URL_KEY
import certifi
import os
ca = certifi.where()

class MongoDBClient:
    client = None
    def __init__(self, database_name=DATABASE_NAME) -> None:
        try:

            if MongoDBClient.client is None:
                #mongo_db_url = os.getenv(MONGODB_URL_KEY)
                mongo_db_url  = "mongodb://root:root@ac-r8tidn9-shard-00-00.x62ls89.mongodb.net:27017,ac-r8tidn9-shard-00-01.x62ls89.mongodb.net:27017,ac-r8tidn9-shard-00-02.x62ls89.mongodb.net:27017/?ssl=true&replicaSet=atlas-aaf4ii-shard-0&authSource=admin&retryWrites=true&w=majority"
                MongoDBClient.client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
            self.client = MongoDBClient.client
            self.database = self.client[database_name]
            self.database_name = database_name
        except Exception as e:
            raise e


