import websocket
import rel
import json
import os

KEY_ID = os.getenv("KEY_ID")
KEY_SECRET = os.getenv("KEY_SECRET")

authData = json.dumps({
    "api_key_id": KEY_ID,
    "api_key_secret": KEY_SECRET
})

rel.safe_read()

def on_open(ws):
    ws.send(authData)
    
def on_message(ws, message):
    print(message)
    print("received")
    
def on_close(ws, close_status_code, close_message):
    print("connection closed")

# short-lived connection
ws = websocket.WebSocket()
ws.connect("wss://ws.luno.com/api/1/stream/XBTIDR")
ws.send(authData)
print(ws.recv())
ws.close()

# long-lived connection
websocket.enableTrace(True)
ws = websocket.WebSocketApp("wss://ws.luno.com/api/1/stream/XBTIDR", on_open=on_open, on_message=on_message, on_close=on_close)
ws.run_forever(dispatcher=rel)
rel.signal(2, rel.abort)
rel.dispatch()