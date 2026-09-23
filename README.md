# Python HTTP Server From Scratch
 
A minimal HTTP/1.1 server written in Python directly on top of TCP sockets, with no web framework and no `http.server`. It reads and parses raw requests, serves static files from a sandboxed document root, blocks directory traversal, and builds every response by hand: status line, headers, and body.
 
The goal is to show what frameworks like Flask or FastAPI handle for you: request framing, `Content-Length`, status codes, and keeping file access inside a web root.
 
## Features
 
- Raw socket server on port 8000 (`socket.AF_INET`, `SOCK_STREAM`, `SO_REUSEADDR`)
- Request parsing: reads until `\r\n\r\n`, splits the request line and headers, then keeps reading the body until it reaches `Content-Length`
- Static file serving from `src/htdocs/`, including nested directories
- `/` maps to `/index.html`
- `GET /health` route that returns a status payload
- Directory traversal protection: resolved paths outside `htdocs/` get a `403`
- Status codes: `200`, `400`, `403`, `404`, `500`
- `Content-Length` is computed from the actual byte length of the body, so UTF-8 and emoji content is sent correctly
- `Content-Type: text/html; charset=utf-8` for HTML and `application/octet-stream` for everything else
- `Connection: close` on every response; each socket is closed in a `finally` block, even when an error occurs
## How a request is handled
 
```
accept() ──▶ readHTTPReq ──▶ parseRequestLine ──▶ routeRequest ──▶ sendResponse ──▶ close()
               │                 │                    │
               │                 └─ malformed ──▶ 400 │
               └─ no header terminator ──▶ 400        ├─ /health ──▶ 200
                                                      ├─ outside htdocs ──▶ 403
                                                      ├─ missing file ──▶ 404
                                                      └─ file ──▶ 200
```
 
Any exception raised while handling a request becomes a `500 Internal Server Error`.
 
## Project structure
 
```
src/
  main.py          # socket setup and accept loop
  functions.py     # request reading/parsing, routing, response building
  htdocs/          # document root
    index.html
    ipsum.html
    deep.html              # large page, for checking Content-Length on bigger bodies
    unicode.html           # multilingual text and emoji, for checking UTF-8 handling
    links.html             # links to each route
    notfound-test.html     # link to a missing page, for the 404 path
    subdir/
      nested.html          # nested directory serving
Dockerfile
```
 
## Running it
 
Requires Python 3. No dependencies.
 
```bash
cd src
python main.py
```
 
Open `http://localhost:8000`, or use curl:
 
```bash
$ curl -i localhost:8000/
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 209
Connection: close
...
 
$ curl -s -o /dev/null -w "%{http_code}\n" localhost:8000/subdir/nested.html
200
 
$ curl -s -o /dev/null -w "%{http_code}\n" localhost:8000/nope.html
404
 
# --path-as-is stops curl from normalizing the ../ before sending it
$ curl -s --path-as-is -o /dev/null -w "%{http_code}\n" localhost:8000/../functions.py
403
```
 
### With Docker
 
```bash
docker build -t python-httpserver .
docker run -p 8000:8000 python-httpserver
```
 
## Limitations
 
This is a learning project and supports only a subset of HTTP/1.1:
 
- One connection at a time: the accept loop is single-threaded and blocking.
- No keep-alive, chunked transfer encoding, or `Host` header validation.
- Methods aren't checked, so a `POST` to a file path serves the file the same way `GET` does. There's no `405` response.
- Query strings aren't stripped, so `/index.html?x=1` returns a `404`.
- Content types cover HTML only; CSS, JS, and images are sent as `application/octet-stream`.
- `/health` returns `{'status':'ok'}` with single quotes, which isn't valid JSON even though the response is labelled `application/json`.
- The traversal check compares string prefixes (`startswith`), so a sibling directory whose name starts with `htdocs` (for example `htdocs-private/`) would get through. `Path.is_relative_to(ROOT)` would close that gap.
