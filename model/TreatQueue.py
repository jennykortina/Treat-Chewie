import datetime
import logging
import time
from dateutil.parser import parse

from collections import defaultdict

from pymongo import ASCENDING, DESCENDING
from pymongo.objectid import ObjectId
from model.MongoMixIn import MongoMixIn

from lib.utils import get_this_hour_dt, format_datetime_for_printing

class TreatQueue(MongoMixIn):
    MONGO_DB_NAME = "treat_queue"
    MONGO_COLLECTION_NAME = "tq"

    A_ID                = '_id'
    A_NAME              = 'name'
    A_PHONE             = 'phone'
    A_TREAT_TIME        = 'treat_time'      # year-month-day-hour e.g. 2011-10-23-24
    A_PRETTY_HOUR       = 'pretty_hour'      # formatted for printing
    A_STATUS            = 'status'
    A_TIMESTAMP_CREATED = 'ts_created'
    A_TIMESTAMP_UPDATED = 'ts_updated'

    STATUS_PENDING      = 1
    STATUS_COMPLETED    = 2
    STATUS_FAILED       = 3
    STATUS_CANCELLED    = 4

    TREAT_TIME_FORMAT   = '%Y-%m-%d-%H'

    TREAT_DAYS_START    = 1
    TREAT_DAYS_END      = 5
    TREAT_HOURS_START   = 10
    TREAT_HOURS_END     = 17

    @classmethod
    def setup_mongo_indexes(klass):
        klass.mdbc().ensure_index([(klass.A_TREAT_TIME, ASCENDING)], unique=True)
        klass.mdbc().ensure_index([(klass.A_PHONE, ASCENDING)], unique=False)
        klass.mdbc().ensure_index([(klass.A_STATUS, ASCENDING),
                                   (klass.A_TREAT_TIME, ASCENDING)], unique=False)

    @classmethod
    def add_to_queue(klass, name, phone, treat_time=None):
        if not treat_time:
            treat_time = klass.get_next_open_treat_slot()
        treat_time_string = datetime.datetime.strftime(treat_time, 
                                                       klass.TREAT_TIME_FORMAT)
        doc = {
            klass.A_NAME: name,
            klass.A_PHONE: phone,
            klass.A_TREAT_TIME: treat_time_string,
            klass.A_STATUS: klass.STATUS_PENDING,
            klass.A_TIMESTAMP_CREATED: int(time.time())
        }
        try:
            klass.mdbc().insert(doc)
            return format_datetime_for_printing(treat_time)
        except Exception, e:
            logging.error("[TreatChewie.add_to_queue] Error: %s" % e)
            return False

    @classmethod
    def complete_treat(klass, treat_id, new_status):
        if type(treat_id) in [str, unicode]:
            treat_id = ObjectId(treat_id)
        spec = {
            klass.A_ID: treat_id
        }
        doc = {
            klass.A_STATUS: new_status,
            klass.A_TIMESTAMP_UPDATED: int(time.time())
        }
        document = {"$set": doc}
        try:
            resp = klass.mdbc().update(spec, document, upsert=True, safe=True)
            return resp
        except Exception, e:
            logging.error("[TreatChewie.complete_treat] Error: %s" % e)
            return False

    @classmethod
    def get_next_treat(klass, get_latest=False):
        this_hour = datetime.datetime.strftime(get_this_hour_dt(),
                                               klass.TREAT_TIME_FORMAT)
        spec = {
            klass.A_STATUS: klass.STATUS_PENDING,
            klass.A_TREAT_TIME: {
                "$gte":this_hour
            }
        }
        if get_latest:
            sort = [(klass.A_TREAT_TIME, DESCENDING)]
        else:
            sort = [(klass.A_TREAT_TIME, ASCENDING)]
        treat = klass.mdbc().find(spec).sort(sort).limit(1)
        treat = [x for x in treat]
        if treat and len(treat) == 1: 
            return treat[0]
        else:
            return None

    @classmethod
    def get_current_treat(klass):
        this_hour = datetime.datetime.strftime(get_this_hour_dt(),
                                               klass.TREAT_TIME_FORMAT)
        spec = {
            klass.A_STATUS: klass.STATUS_PENDING,
            klass.A_TREAT_TIME: this_hour
        }
        return klass.mdbc().find_one(spec)

    @classmethod
    def get_latest_treat(klass):
        return klass.get_next_treat(get_latest=True)

    @classmethod
    def get_next_treat_time(klass, get_latest=False):
        next_treat = klass.get_next_treat(get_latest=get_latest)
        if next_treat:
            next_treat_time = next_treat.get(klass.A_TREAT_TIME)
            next_treat_time = datetime.datetime.strptime(next_treat_time,
                                                         klass.TREAT_TIME_FORMAT)
            return next_treat_time
        return None

    @classmethod
    def get_next_open_treat_slot(klass):
        next_treat_time = klass.get_next_treat_time(get_latest=True)
        if not next_treat_time:
            next_treat_time = datetime.datetime.now().replace(minute=0, 
                                                              second=0,
                                                              microsecond=0)
        next_treat_slot = next_treat_time + datetime.timedelta(hours=1)
        if next_treat_slot.hour < klass.TREAT_HOURS_START:
            next_treat_slot = next_treat_slot.replace(hour=klass.TREAT_HOURS_START)
        if next_treat_slot.hour > klass.TREAT_HOURS_END:
            next_treat_slot = next_treat_slot.replace(hour=klass.TREAT_HOURS_START)
            next_treat_slot = next_treat_slot + datetime.timedelta(days=1)
            if int(next_treat_slot.strftime('%w')) > klass.TREAT_DAYS_END:
                next_treat_slot = next_treat_slot + datetime.timedelta(days=2)
        return next_treat_slot

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

    @classmethod
    def get_treat_queue(klass):
        now = datetime.datetime.now()
        beginning_of_week = now - datetime.timedelta(
            int(now.strftime('%w')))
        beginning_of_week = beginning_of_week.strftime('%Y-%m-%d')
        spec = {
            klass.A_TREAT_TIME: {
                "$gt":beginning_of_week
            }
        }
        sort = [(klass.A_TREAT_TIME, ASCENDING)]
        cursor = klass.mdbc().find(spec).sort(sort)
        treats = [treat for treat in cursor]
        tq = defaultdict(lambda: list())
        tq = list()
        for t in treats:
            del t['_id']
            del t[klass.A_PHONE]
            treat_time = t.get(klass.A_TREAT_TIME)
            treat_d = parse(treat_time[:10])
            day = treat_d.day
            format_string = '%s, %s %s' % ('%A', '%B', day)
            treat_d = treat_d.strftime(format_string)
            treat_dt = parse(treat_time)
            hour = treat_dt.hour
            ampm = treat_dt.strftime('%p').lower()
            t[klass.A_PRETTY_HOUR] = "%s%s" % (hour, ampm)
            if (not tq or 
                tq and tq[-1].get('date') != treat_d):
                item = {
                    'date':treat_d,
                    'data':[t]
                }
                tq.append(item)
            else:
                tq[-1]['data'].append(t)
        return tq
