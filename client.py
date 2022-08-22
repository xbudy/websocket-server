from websocket import create_connection

ws = create_connection("wss://python-socket-api.herokuapp.com/ws", header = ["client-id: 1"])
print("Connection established")
while True:
    try:
        result = ws.recv()
        if result == "ALREADY CONNECTED":
            print(result)
            ws.close()
            break
        if result == "UPDATE":
            pass
        print("Received: {}".format(result))
    except KeyboardInterrupt:
        ws.close()
        print("Connection closed")
        exit(0)