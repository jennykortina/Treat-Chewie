import os
import logging
import re
import simplejson

import settings

import tornado.auth
import tornado.ioloop
import tornado.web

from model.TreatQueue import TreatQueue

from lib.utils import format_valid_phone_number, format_datetime_for_printing


class AuthMixin():
    def authenticate_user(self):
        session_email = self.get_secure_cookie('session_email')
        if not session_email:
            self.redirect('/auth')
            return False
        if not self.is_session_email_authorized(session_email):
            self.clear_cookie('session_email')
            self.write('Sorry, you do not have access to this page')
            return False
        return True

    def is_session_email_authorized(self, email):
        allowed_email_regex = getattr(settings, 
                                      'ALLOWED_EMAIL_REGEX',
                                      None)
        if allowed_email_regex:
            if re.match(allowed_email_regex, email):
                return True
        if hasattr(settings, 'ALLOWED_EMAILS'):
            if email in settings.ALLOWED_EMAILS:
                return True
        return False


class BaseHandler(tornado.web.RequestHandler):
    pass


class MainHandler(BaseHandler):
    def get(self):
        next_treat_time = TreatQueue.get_next_treat_time()
        if next_treat_time:
            next_treat_time = format_datetime_for_printing(next_treat_time)
        else:
            next_treat_time = "No treats scheduled :( Give the next treat!"
        next_treat_slot = TreatQueue.get_next_open_treat_slot()
        next_treat_slot = format_datetime_for_printing(next_treat_slot)
        self.render("templates/index.html", 
                    next_treat_time=next_treat_time,
                    next_treat_slot=next_treat_slot)


class AddTreatHandler(BaseHandler):
    def post(self):
        success = False
        error = None
        phone = self.get_argument('phone')
        name = self.get_argument('name')
        phone = format_valid_phone_number(phone)
        if phone and name:
            latest_treat = TreatQueue.get_latest_treat()
            if latest_treat and latest_treat.get(TreatQueue.A_PHONE) == phone:
                error = 'duplicate'
            else:
                next_treat_slot = TreatQueue.get_next_open_treat_slot()
                treat_time = TreatQueue.add_to_queue(name, phone, next_treat_slot)
                if treat_time:
                    success = True
                else:
                    error = 'other_error'
        else:
            error = 'missing_param'
        
        if success:
            resp = {
                'success':1,
                'treat_time': treat_time
            }
        elif error == "missing_param":
            resp = {
                'error': 1,
                'message': 'Either first_name or phone_number were not provided'
            }
        elif error == "duplicate":
            resp = {
                'error': 1,
                'message': 'Sorry, you can\'t sign up for two treats in a row'
            }
        elif error == "other_error":
            resp = {
                'error': 1,
                'message': 'Sorry, there was an error adding you to the queue'
            }

        self.write(resp)

    def get(self):
        pass


class QueueHandler(BaseHandler):
    def get(self):
        treat_queue = TreatQueue.get_treat_queue()
        self.write(simplejson.dumps(treat_queue))


class BackdoorHandler(BaseHandler, AuthMixin):
    def get(self):
        if self.authenticate_user():
            self.render('templates/backdoor.html')

    def post(self):
        # post to call a specific phone number
        phone = self.get_argument('phone', default=None)
        if phone:
            from lib import facetime
            facetime.make_call(phone)
            self.write(1)

        # post to dispense a treat
        dispense = self.get_argument('dispense', default=None)
        if dispense:
            from lib import dispense_treat
            dispense_treat.run_arduino()
            self.write(1)

class AuthHandler(BaseHandler, tornado.auth.GoogleMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("openid.mode", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authenticate_redirect()

    def _on_auth(self, user):
        if not user:
            raise tornado.web.HTTPError(500, "Google auth failed")
        # Save the authenticated user's details in a secure cookie
        self.set_secure_cookie('session_email', user.get('email'))
        self.redirect('/backdoor')


app_settings = {
    'static_path': os.path.join(os.path.dirname(__file__), "static"),
    'cookie_secret': settings.COOKIE_SECRET
}

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/add", AddTreatHandler),
    (r"/backdoor", BackdoorHandler),
    (r"/auth", AuthHandler),
    (r"/queue", QueueHandler),
    (r"/static/.*", tornado.web.StaticFileHandler)
], **app_settings)

if __name__ == "__main__":
    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()
