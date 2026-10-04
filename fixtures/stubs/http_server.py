#!/usr/bin/env python3
"""Socket-free local HTTP server fixture using the standard library handler."""
from http.server import BaseHTTPRequestHandler
import io
import json
from pathlib import Path
import sys


class Socket:
    def __init__(self, data):
        self.input = io.BytesIO(data)
        self.output = io.BytesIO()

    def makefile(self, *args, **kwargs):
        return self.input

    def sendall(self, data):
        self.output.write(data)


def respond(body, response):
    """Return a real HTTP response byte stream without opening a network socket."""
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            incoming = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            if incoming != body:
                raise AssertionError("Request body changed in transport")
            encoded = json.dumps(response).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, *args):
            pass

    encoded = json.dumps(body).encode()
    request = (b"POST /v1/chat/completions HTTP/1.0\r\nHost: 127.0.0.1\r\nContent-Length: "
               + str(len(encoded)).encode() + b"\r\n\r\n" + encoded)
    socket = Socket(request)
    Handler(socket, ("127.0.0.1", 0), None)
    return socket.output.getvalue()


if __name__ == "__main__":
    body = json.load(sys.stdin)
    replies = json.loads((Path(__file__).parents[1] / "completions.json").read_text())["example-model"]
    response = replies[0 if body.get("max_tokens") == 20000 else 1]
    sys.stdout.buffer.write(respond(body, response))
