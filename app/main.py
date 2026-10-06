"""Northfield status service. Health, metrics, optional fail mode."""
from __future__ import annotations

import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

START = time.time()
REQUESTS = 0
FAIL = os.environ.get("STATUS_FAIL", "0") == "1"
VERSION = os.environ.get("APP_VERSION", "1.0.0")


def health_body() -> tuple[int, bytes]:
    if FAIL:
        return 503, b'{"status":"fail","reason":"STATUS_FAIL=1"}\n'
    return 200, b'{"status":"ok"}\n'


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        global REQUESTS
        REQUESTS += 1
        if self.path in ("/", "/health"):
            code, body = health_body()
            self._send(code, "application/json", body)
            return
        if self.path == "/ready":
            code, body = health_body()
            self._send(code, "application/json", body)
            return
        if self.path == "/metrics":
            up = time.time() - START
            health = 0 if FAIL else 1
            body = (
                f"# HELP northfield_up 1 if the process is up\n"
                f"# TYPE northfield_up gauge\n"
                f"northfield_up 1\n"
                f"# HELP northfield_health 1 if /health is ok\n"
                f"# TYPE northfield_health gauge\n"
                f"northfield_health {health}\n"
                f"# HELP northfield_requests_total HTTP requests\n"
                f"# TYPE northfield_requests_total counter\n"
                f"northfield_requests_total {REQUESTS}\n"
                f"# HELP northfield_uptime_seconds process uptime\n"
                f"# TYPE northfield_uptime_seconds gauge\n"
                f"northfield_uptime_seconds {up:.0f}\n"
            ).encode()
            self._send(200, "text/plain; version=0.0.4", body)
            return
        self.send_error(404)

    def _send(self, code: int, ctype: str, body: bytes) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-App-Version", VERSION)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        sys_stderr = __import__("sys").stderr
        sys_stderr.write("status-service %s\n" % (fmt % args))


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
