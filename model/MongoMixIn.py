class MongoMixIn():

    @classmethod
    def mdbc(klass):
        """ returns a pointer to the DB collection"""
        if not getattr(klass, 'MDBC', None):
            from pymongo.connection import Connection
            connection = Connection()
            db = connection[klass.MONGO_DB_NAME]
            klass.MDBC = db[klass.MONGO_COLLECTION_NAME]
        return klass.MDBC
 
