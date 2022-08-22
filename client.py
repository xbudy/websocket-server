from websocket import create_connection

ws = create_connection("ws://localhost:9000", header = ["client-id: 1"])
print("Connection established")
while True:
    try:
        result = ws.recv()
        if result == "ALREADY CONNECTED":
            print(result)
            ws.close()
            break
        print("Received: {}".format(result))
    except KeyboardInterrupt:
        ws.close()
        print("Connection closed")
        exit(0)