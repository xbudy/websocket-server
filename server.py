from time import sleep
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource
from autobahn.twisted.resource import WebSocketResource
from twisted.web.static import Data, File
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS

import os

class BroadcastServerProtocol(WebSocketServerProtocol):
    def onOpen(self):
        self.factory.register(self)

    def onConnect(self, request):
        self.client_id = request.headers['client-id']

        print("Client connecting: {}".format(request.peer))

    def onMessage(self, payload, isBinary):
        if not isBinary:
            if (msg := payload.decode("utf-8")).startswith("@a"):
                self.factory.broadcast("Got message: " + msg)

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)


class BroadcastServerFactory(WebSocketServerFactory):
    def __init__(self):
        WebSocketServerFactory.__init__(self)
        self.clients = {}

    def register(self, client):
        print(self.clients)
        if client.client_id not in self.clients.keys():
            print("registered client {}".format(client.peer))
            self.clients[client.client_id] = client
        else:
            client.client_id = None
            client.sendMessage("ALREADY CONNECTED".encode('utf-8'))

    def unregister(self, client):
        if client.client_id in self.clients:
            print("unregistered client {}".format(client.peer))
            self.clients.pop(client.client_id)

    def broadcast(self, msg, client_id = None):
        if not client_id:
            print("broadcasting message '{}' to {} clients ...".format(msg, len(self.clients)))
            for c in self.clients:
                c.sendMessage(msg.encode('utf-8'))
        else:
            if client_id in self.clients:
                self.clients[client_id].sendMessage(msg.encode('utf-8'))


class apiPage(Resource):
    def __init__(self, w: BroadcastServerFactory):
        super().__init__()
        self.factory = w
    def render_GET(self, request):
        print(self.factory.clients)
        return '<html><body><form method="POST"><input name="the-field" type="text" /></form></body></html>'

    def render_POST(self, request):
        self.factory.broadcast("hi", client_id=dict(request.args)[b"client-id"][0].decode("utf-8"))
        return ('<html><body>You submitted: %s</body></html>' % dict(request.args)[b"client-id"][0].decode("utf-8")).encode()


if __name__ == "__main__":
    ServerFactory = BroadcastServerFactory
    factory = ServerFactory()
    factory.protocol = BroadcastServerProtocol
    r = WebSocketResource(factory)
    root = Resource()
    root.putChild(b"api", apiPage(factory))
    root.putChild(b"ws", r)
    web = Site(root)
    reactor.listenTCP(int(os.getenv("PORT")), web)

    reactor.run()