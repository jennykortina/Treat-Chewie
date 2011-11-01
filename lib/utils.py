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
    if datetime.datetime.now().date() == dt.date():
        format = "%I%p today"
    else:
        format = "%I%p on %A"
    return dt.strftime(format)

def get_this_hour_dt():
    return datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
