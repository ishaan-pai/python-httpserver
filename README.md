Minimal HTTP Server (Python)

A lightweight HTTP/1.1 web server implemented from scratch in Python using raw TCP sockets.
This project focuses on protocol correctness, security, and backend fundamentals, without relying on web frameworks.

Features
- HTTP/1.1–compliant request handling
- Static file serving from a constrained document root
- Nested directory support
- Custom application routes (e.g. /health)
- Directory traversal protection (../ prevention)
- Proper status codes (200, 403, 404, 400)
- Correct response headers (Content-Type, Content-Length, Connection)
- UTF-8 and Unicode-safe content delivery
- Graceful connection termination

Project Structure
src/
  main.py         
  functions.py      
  htdocs/
    index.html
    ipsum.html
    unicode.html
    deep.html
    subdir/
      nested.html
