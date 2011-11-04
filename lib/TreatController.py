import sys
sys.path.append("../")
import logging
import time

from lib import facetime
from lib import dispense_treat
from lib.twilio_helper import TwilioHelper
from lib.utils import format_valid_phone_number

from model.TreatQueue import TreatQueue

class TreatController():
    @classmethod
    def dispense_treat(klass, phone_to_call=None):
        # find the treat for this hour
        treat_doc = None
        if not phone_to_call:
            treat_doc = TreatQueue.get_current_treat()
            if treat_doc:
                phone_to_call = treat_doc.get(TreatQueue.A_PHONE)
            else:
                # no treat for this hour - so do we dispense?
                print "no treats to give this hour. exiting."
                return
        else:
            phone_to_call = format_valid_phone_number(phone_to_call)

        # place facetime call
        facetime.make_call(phone_to_call)
        time.sleep(30)

        # dispense treat
        try:
            dispense_treat.run_arduino()
        except Exception, e:
            logging.error("[TreatController.dispense_treat] Error: %s" % e)

        # mark treat as dispensed
        if treat_doc:
            TreatQueue.complete_treat(treat_doc.get(TreatQueue.A_ID),
                                      TreatQueue.STATUS_COMPLETED)

    @classmethod
    def send_text_reminder(klass, treat_doc=None):
        # get the next treat's details
        if not treat_doc:
            treat_doc = TreatQueue.get_current_treat()
        # if there is one, send that person a text to remind them that it's their turn
        if treat_doc:
            phone = treat_doc.get(TreatQueue.A_PHONE)
            name = treat_doc.get(TreatQueue.A_NAME)
            message = ("Hi %s, it's almost time to treat me! "
                       "I'll call you in 10 minutes, so please make sure you're "
                       "connected to wifi. See you soon!" % name)
            TwilioHelper.send_sms(phone, message)
        else:
            print "no treats to give this hour."

