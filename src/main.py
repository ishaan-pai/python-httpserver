"""
 Implements a simple HTTP/1.1 Server

"""

import socket
from functions import (
    readHTTPReq as readReq,
    parseRequestLine as parseLine,
    routeRequest,
    sendResponse
)

SOCK_ADDR = "0.0.0.0"
SOCK_PORT = 8000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((SOCK_ADDR, SOCK_PORT))

server_socket.listen(5)
print('Listening on port %s ...' % SOCK_PORT)

while True:
    client_connection, client_address = server_socket.accept()

    try:
        requestLine, headers, body = readReq(client_connection)
        if not requestLine:
            sendResponse(client_connection, 400, {"Content-Type": "text/plain"}, b"400 Bad Request")
        else:
            method, path, version = parseLine(requestLine)
            if not method:
                sendResponse(client_connection, 400, {"Content-Type": "text/plain"}, b"400 Bad Request")
            else:
                status, respHeaders, respBody = routeRequest(method, path, headers, body)
                sendResponse(client_connection, status, respHeaders, respBody)

    except Exception:
        sendResponse(client_connection, 500, {"Content-Type": "text/plain"}, b"Internal Server Error")

    finally:
        client_connection.close()

server_socket.close()
