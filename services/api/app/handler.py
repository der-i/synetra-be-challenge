import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

from db import Database

REQUIRED_FIELDS = ("image_url", "width", "height")


def make_handler(db: Database):
  class ObjectsHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload) -> None:
      body = json.dumps(payload).encode("utf-8")
      self.send_response(status)
      self.send_header("Content-Type", "application/json")
      self.send_header("Access-Control-Allow-Origin", "*")
      self.send_header("Content-Length", str(len(body)))
      self.end_headers()
      self.wfile.write(body)

    def _read_json(self) -> dict:
      length = int(self.headers.get("Content-Length", 0))
      raw = self.rfile.read(length) if length else b"{}"
      return json.loads(raw)

    def do_OPTIONS(self) -> None:
      self.send_response(204)
      self.send_header("Access-Control-Allow-Origin", "*")
      self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
      self.send_header("Access-Control-Allow-Headers", "Content-Type")
      self.end_headers()

    def do_POST(self) -> None:
      if urlparse(self.path).path != "/objects":
        self._send_json(404, {"error": "not found"})
        return
      try:
        payload = self._read_json()
      except json.JSONDecodeError:
        self._send_json(400, {"error": "invalid json"})
        return

      missing = [f for f in REQUIRED_FIELDS if f not in payload]
      if missing:
        self._send_json(400, {"error": f"missing fields: {missing}"})
        return

      try:
        image_url = str(payload["image_url"])
        width = int(payload["width"])
        height = int(payload["height"])
      except (TypeError, ValueError):
        self._send_json(400, {"error": "width/height must be integers"})
        return

      record = db.create(image_url, width, height)
      self._send_json(201, record)

    def do_GET(self) -> None:
      path = urlparse(self.path).path

      if path == "/objects":
        self._send_json(200, db.list())
        return

      if path.startswith("/objects/"):
        raw_id = path.removeprefix("/objects/")
        if not raw_id.isdigit():
          self._send_json(400, {"error": "id must be an integer"})
          return
        record = db.get(int(raw_id))
        if record is None:
          self._send_json(404, {"error": "not found"})
          return
        self._send_json(200, record)
        return

      self._send_json(404, {"error": "not found"})

    def log_message(self, fmt: str, *args) -> None:
      print(f"{self.address_string()} - {fmt % args}")

  return ObjectsHandler