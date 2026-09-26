import threading
from http.server import ThreadingHTTPServer

import pytest
import requests
from db import Database
from handler import make_handler


@pytest.fixture()
def api_server(tmp_path):
  db = Database(str(tmp_path / "test.db"))
  server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(db))
  thread = threading.Thread(target=server.serve_forever, daemon=True)
  thread.start()

  port = server.server_address[1]
  yield f"http://127.0.0.1:{port}"

  server.shutdown()
  thread.join()


def test_create_and_get(api_server):
  create_resp = requests.post(
    f"{api_server}/objects",
    json={"image_url": "http://x/1.png", "width": 100, "height": 200},
  )
  assert create_resp.status_code == 201
  record = create_resp.json()
  assert record["image_url"] == "http://x/1.png"
  assert record["width"] == 100
  assert record["height"] == 200

  get_resp = requests.get(f"{api_server}/objects/{record['id']}")
  assert get_resp.status_code == 200
  assert get_resp.json() == record


def test_list_returns_all_created_records(api_server):
  for i in range(3):
    requests.post(
      f"{api_server}/objects",
      json={"image_url": f"http://x/{i}.png", "width": 10, "height": 20},
    )

  list_resp = requests.get(f"{api_server}/objects")
  assert list_resp.status_code == 200
  assert len(list_resp.json()) == 3


def test_missing_fields_returns_400(api_server):
  resp = requests.post(f"{api_server}/objects", json={"image_url": "x"})
  assert resp.status_code == 400


def test_non_integer_width_returns_400(api_server):
  resp = requests.post(
    f"{api_server}/objects",
    json={"image_url": "x", "width": "abc", "height": 1},
  )
  assert resp.status_code == 400


def test_get_nonexistent_id_returns_404(api_server):
  resp = requests.get(f"{api_server}/objects/9999")
  assert resp.status_code == 404


def test_get_non_integer_id_returns_400(api_server):
  resp = requests.get(f"{api_server}/objects/not-a-number")
  assert resp.status_code == 400