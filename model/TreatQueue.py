import datetime
import logging
#import time

from pymongo.objectid import ObjectId
from model.MongoMixIn import MongoMixIn

class TreatQueue(MongoMixIn):
    MONGO_DB_NAME = "treat_queue"
    MONGO_COLLECTION_NAME = "tq"

    A_ID                = '_id'
    A_PHONE             = 'phone'
    A_TREAT_TIME        = 'treat_time'      # year-month-day-hour e.g. 2011-10-23-24
    A_STATUS            = 'status'

    STATUS_PENDING      = 1
    STATUS_COMPLETED    = 2
    STATUS_FAILED       = 3
    STATUS_CANCELLED    = 4

    TREAT_TIME_FORMAT   = '%Y-%m-%d-%H'

    @classmethod
    def setup_mongo_indexes(klass):
        from pymongo import ASCENDING
        klass.mdbc().ensure_index([(klass.A_TREAT_TIME, ASCENDING)], unique=True)
        klass.mdbc().ensure_index([(klass.A_PHONE, ASCENDING)], unique=False)
        klass.mdbc().ensure_index([(klass.A_STATUS, ASCENDING),
                                   (klass.A_TREAT_TIME, ASCENDING)], unique=False)

    @classmethod
    def add_to_queue(klass, phone, treat_time=None):
        if not treat_time:
            now = datetime.datetime.now()
            treat_time = now + datetime.timedelta(hours=1)
            treat_time = datetime.datetime.strftime(treat_time, 
                                                    klass.TREAT_TIME_FORMAT)
        doc = {
            klass.A_PHONE: phone,
            klass.A_TREAT_TIME: treat_time,
            klass.A_STATUS: klass.STATUS_PENDING
        }
        try:
            return klass.mdbc().insert(doc)
        except Exception, e:
            logging.error("[TreatChewie.add_to_queue] Error: %s" % e)
            return 

    @classmethod
    def complete_treat(klass, treat_id, new_status):
        spec = {klass.A_ID: treat_id}
        doc = {klass.A_STATUS: new_status}
        document = {"$set": doc}
        try:
            resp = klass.mdbc().update(spec, document, upsert=True, safe=True)
            return resp
        except Exception, e:
            logging.error("[TreatChewie.complete_treat] Error: %s" % e)
            return False

    @classmethod
    def get_next_treat(klass):
        spec = {
            klass.A_STATUS: klass.STATUS_PENDING
        }
        # TODO: complete
        return klass.mdbc().find_one(spec)

    @classmethod
    def find_by_treat_time(klass, treat_time):
        spec = {klass.A_TREAT_TIME: treat_time}
        return klass.mdbc().find_one(spec)

    @classmethod
    def find_by_id(klass, treat_id):
        if type(treat_id) in [str, unicode]:
            treat_id = ObjectId(treat_id)
        spec = {klass.A_ID: treat_id}
        return klass.mdbc().find_one(spec)
