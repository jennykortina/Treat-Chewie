import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
	self.render("templates/chewie.html")

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/static/.*", tornado.web.StaticFileHandler)
])

if __name__ == "__main__":
    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()
