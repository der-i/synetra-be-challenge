import os
import sys
from http.server import ThreadingHTTPServer

from dotenv import load_dotenv
from db import Database
from handler import make_handler


def main():
  try:
    load_dotenv()
    port = int(os.getenv("API_PORT", 8000))
    sqlite_path = os.getenv("SQLITE_PATH", "/data/sqlite/excercise.db")

    db = Database(sqlite_path)
    handler_cls = make_handler(db)

    server = ThreadingHTTPServer(("0.0.0.0", port), handler_cls)
    print(f"API listening on 0.0.0.0:{port}, db at {sqlite_path}")
    server.serve_forever()
  except Exception as e:
    print(f"Error occurred: {e}")
    sys.exit(1)


if __name__ == "__main__":
  main()