from pathlib import Path

ROOT = (Path(__file__).resolve().parent / "htdocs").resolve()

def readHTTPReq(sock) -> tuple:
    buffer = b""

    while b"\r\n\r\n" not in buffer:
        chunk = sock.recv(1024)
        if not chunk:
            break
        buffer += chunk

    if b"\r\n\r\n" not in buffer:
        return (None, {}, b"")
    
    headerBytes, body = buffer.split(b"\r\n\r\n", 1)
    headerText = headerBytes.decode("utf-8", errors="replace")
    headerTextLines = headerText.split("\r\n")

    serverRequestLine = headerTextLines[0]

    headers = {}
    for line in headerTextLines[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip()] = value.strip()

    contentLength = int(headers.get("Content-Length", "0"))
    while len(body) < contentLength:
        chunk = sock.recv(1024)
        if not chunk:
            break
        body += chunk

    return (serverRequestLine, headers, body)

def parseRequestLine(requestLine) -> tuple:
    parts = requestLine.split()
    if len(parts) < 3:
        return (None, None, None)
    return tuple(parts)

"""
note: headers and body isn't necessary for this function (currently unused) but
in case the program is updated to connect to an actual backend, its good to 
have the inputs already there anyways.
"""
def routeRequest(method, path, headers, body) -> tuple:
    if method == "GET" and path == "/health":
        responseBody = b"{'status':'ok'}"
        return (200, {"Content-Type": "application/json"}, responseBody)
    
    if path == "/":
        path = "/index.html"

    requested = (ROOT / path.lstrip("/")).resolve()
    if not str(requested).startswith(str(ROOT)):
        responseBody = b"403 Forbidden"
        return (403, {"Content-Type": "text/plain"}, responseBody)
    if not requested.exists() or not requested.is_file():
        responseBody = b"404 Not Found"
        return (404, {"Content-Type": "text/plain"}, responseBody)
    responseBody = requested.read_bytes()

    if requested.suffix == ".html":
        contentType = "text/html; charset=utf-8"
    else:
        contentType = "application/octet-stream"

    return (200, {"Content-Type": contentType}, responseBody)

def sendResponse(sock, statusCode, headers, body):

    reason = {
        200: "OK",
        403: "Forbidden",
        404: "Not Found",
        400: "Bad Request",
        500: "Internal Server Error"
    }.get(statusCode, "OK")

    headers = dict(headers)
    headers["Content-Length"] = str(len(body))
    headers["Connection"] = "close"

    statusLine = f"HTTP/1.1 {statusCode} {reason}\r\n"
    headerLines = ""
    for key, value in headers.items():
        headerLines += f"{key}: {value}\r\n"
    responseBytes = (statusLine + headerLines + "\r\n").encode("utf-8") + body

    sock.sendall(responseBytes)
