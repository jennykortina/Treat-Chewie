import sys
sys.path.append("../")
import re

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
