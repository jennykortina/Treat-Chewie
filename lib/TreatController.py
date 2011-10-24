import sys
sys.path.append("../")
import logging
import time

from lib import facetime
from lib import dispense_treat
from lib.utils import format_valid_phone_number

from model.TreatQueue import TreatQueue

class TreatController():
    @classmethod
    def dispense_treat(klass, phone_to_call=None):
        # find the treat for this hour
        treat_doc = None
        if not phone_to_call:
            treat_doc = TreatQueue.get_next_treat()
            if treat_doc:
                phone_to_call = treat_doc.get(TreatQueue.A_PHONE)
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
