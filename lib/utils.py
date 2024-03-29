import sys
sys.path.append("../")
import re
import datetime

def format_valid_phone_number(phone):
    if isinstance(phone, int) or isinstance(phone, unicode):
        phone = str(phone)
    if isinstance(phone, str):
        # remove all non-digits
        phone = re.sub(r'\D', '', phone)
        # check for valid 11 digit phone number
        if len(phone) == 10:
            phone = "1" + phone
        if len(phone) == 11 and phone[1] not in ['0', '1'] and phone[1:4] != '999':
            return phone
    return False

def format_datetime_for_printing(dt):
    now = datetime.datetime.now()
    ampm = dt.strftime('%p').lower()
    hour = dt.strftime('%I').lstrip('0')
    day = dt.strftime('%d').lstrip('0')
    if now.date() == dt.date():
        format = "%I%p today"
    elif now.strftime("%U") == dt.strftime("%U"):
        # if the date is in this week, only show the name of the day
        format = "%s%s on %s" % (hour, ampm, '%A')
    else:
        # otherwise show the day and month too
        format = "%s%s on %s, %s %s" % (hour, ampm, '%A', '%B', day)
    return dt.strftime(format)

def get_this_hour_dt(next_hour_if_10_past_hour=True):
    now = datetime.datetime.now()
    if next_hour_if_10_past_hour and now.minute > 10:
        now = now + datetime.timedelta(hours=1)
    return now.replace(minute=0, second=0, microsecond=0)
