import os
import logging

import tornado.ioloop
import tornado.web

from model.TreatQueue import TreatQueue

from lib.utils import format_valid_phone_number, format_datetime_for_printing

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
        self.check_xsrf_cookie()
        phone = self.get_argument('phone')
        phone = format_valid_phone_number(phone)
        if phone:
            next_treat_slot = TreatQueue.get_next_open_treat_slot()
            resp = TreatQueue.add_to_queue(phone, next_treat_slot)
            if resp:
                self.write("Added you to the queue at %s" % resp)
            else:
                self.write("Sorry, there was an error")
        else:
            self.write("Invalid phone number")

    def get(self):
        pass

settings = {
    'static_path': os.path.join(os.path.dirname(__file__), "static")
}

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/add", AddTreatHandler),
    (r"/static/.*", tornado.web.StaticFileHandler)
], **settings)

if __name__ == "__main__":
    application.listen(8887)
    tornado.ioloop.IOLoop.instance().start()
