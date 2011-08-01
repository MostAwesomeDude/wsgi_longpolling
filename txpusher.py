from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator
from twisted.web.resource import Resource
from twisted.web.server import Site, NOT_DONE_YET

from txredis.protocol import RedisSubscriber

class Puller(RedisSubscriber):

    request = None

    def messageReceived(self, channel, message):
        if self.request and not self.request.finished:
            self.request.write("<div>Message on %s: '%s'</div>\n"
                % (channel, message))
            if message == "quit":
                self.request.finish()

        # Ugh, Venn logic.
        if message == "quit":
            self.transport.loseConnection()

cc = ClientCreator(reactor, Puller)

class Pusher(Resource):

    isLeaf = True

    def render_GET(self, request):
        d = cc.connectTCP("localhost", 6379)
        @d.addCallback
        def cb(protocol):
            protocol.request = request
            protocol.subscribe("messages")

        request.write(" " * 4096)
        request.write("<!DOCTYPE html><html><head></head><h1>Messages!</h1>\n")
        return NOT_DONE_YET

reactor.listenTCP(1234, Site(Pusher()))
reactor.run()
