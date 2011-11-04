import os
import re

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
            self.redirect('/auth/')
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


class MainHandler(tornado.web.RequestHandler):
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


class AddTreatHandler(tornado.web.RequestHandler):
    def post(self):
        phone = self.get_argument('phone')
        name = self.get_argument('name')
        phone = format_valid_phone_number(phone)
        if phone and name:
            next_treat_slot = TreatQueue.get_next_open_treat_slot()
            treat_time = TreatQueue.add_to_queue(name, phone, next_treat_slot)
            if treat_time:
                resp = {
                    'success':1,
                    'treat_time': treat_time
                }
            else:
                resp = {
                    'error': 1,
                    'message': 'Sorry, there was an error adding you to the queue'
                }
        else:
            resp = {
                'error': 1,
                'message': 'Either first_name or phone_number were not provided'
            }
        self.write(resp)

    def get(self):
        pass


class BackdoorHandler(tornado.web.RequestHandler, AuthMixin):
    def get(self):
        if self.authenticate_user():
            self.render('templates/backdoor.html')

    def post(self):
        # post to call a specific phone number

        # post to dispense a treat
        pass


class AuthHandler(tornado.web.RequestHandler, tornado.auth.GoogleMixin):
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
        self.redirect('/')


app_settings = {
    'static_path': os.path.join(os.path.dirname(__file__), "static")
}

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/add", AddTreatHandler),
    (r"/backdoor", BackdoorHandler),
    (r"/static/.*", tornado.web.StaticFileHandler)
], **app_settings)

if __name__ == "__main__":
    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()
