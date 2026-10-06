"""Tiny stdlib HTTP surface for agents.

GET /tool                                   -> MCP-style tool schema
GET /search?q=remote+go+postgres&audience=agent
GET /profile/p1?audience=company
The audience would come from the caller's verified credentials in production; here it's a query param.
"""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .layer import REQUESTER, TOOL_SCHEMA, load_claims, profile, search
from . import data

CLAIMS = load_claims()


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        raw = json.dumps(body, ensure_ascii=False, indent=1).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        u = urlparse(self.path)
        qs = {k: v[0] for k, v in parse_qs(u.query).items()}
        aud = qs.get("audience", "agent")
        if aud not in REQUESTER:
            return self._send(400, {"error": "audience must be 'agent' or 'company'"})
        if u.path == "/tool":
            return self._send(200, TOOL_SCHEMA)
        if u.path == "/search":
            return self._send(200, {"audience": aud, "results": search(CLAIMS, qs.get("q", ""), aud, int(qs.get("k", 3)))})
        if u.path.startswith("/profile/"):
            pid = u.path.rsplit("/", 1)[-1]
            if pid not in data.TRANSCRIPTS:
                return self._send(404, {"error": "unknown profile"})
            return self._send(200, profile(CLAIMS, pid, aud))
        self._send(404, {"error": "try /tool, /search?q=..., /profile/<id>"})

    def log_message(self, *a):
        pass


def serve(port: int = 8765):
    print(f"serving on http://localhost:{port}  (/tool, /search?q=..., /profile/p1?audience=company)")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
