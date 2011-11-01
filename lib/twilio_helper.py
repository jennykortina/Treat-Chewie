import settings

from twilio.rest import TwilioRestClient

class TwilioHelper(object):
    @classmethod
    def send_sms(klass, phone, message):
        tw = TwilioRestClient(settings.TWILIO_SID, settings.TWILIO_TOKEN)
        from_ = settings.TWILIO_NUMBER
        to = phone
        body = message[0:140]
        try:
            tw.sms.messages.create(to=to, from_=from_, body=body)
            return True
        except Exception, e:
            print e
            print e.read()
            return False
