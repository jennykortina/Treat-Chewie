import tornado.ioloop
import tornado.web
from lib.utils import format_valid_phone_number
from lib.TreatController import TreatController

class MainHandler(tornado.web.RequestHandler):
    def get(self):
	self.render("templates/chewie.html")

class AddTreatHandler(tornado.web.RequestHandler):
    def post(self):
        phone = self.get_argument('phone')
        phone = format_valid_phone_number(phone)
        if phone:
            TreatController.add_treat(phone)

    def get(self):
        pass

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/add", AddTreatHandler),
    (r"/static/.*", tornado.web.StaticFileHandler)
])

if __name__ == "__main__":
    application.listen(8887)
    tornado.ioloop.IOLoop.instance().start()
