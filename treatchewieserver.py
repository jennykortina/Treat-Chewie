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

settings = {
    'static_path': os.path.join(os.path.dirname(__file__), "static")
}

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/add", AddTreatHandler),
    (r"/static/.*", tornado.web.StaticFileHandler)
], **settings)

if __name__ == "__main__":
    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()
