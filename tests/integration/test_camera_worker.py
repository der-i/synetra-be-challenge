import json
import struct
from unittest.mock import MagicMock

import pytest
from worker import Worker


def _make_png(path, width: int, height: int) -> None:
  header = (
    b"\x89PNG\r\n\x1a\n"
    + struct.pack(">I", 13)
    + b"IHDR"
    + struct.pack(">II", width, height)
  )
  path.write_bytes(header)


def _make_worker(images_dir, minio=None, api=None, rabbitmq=None) -> Worker:
  return Worker(
    tcp_host="unused",
    tcp_port=0,
    ws_host="127.0.0.1",
    ws_port=0,
    images_dir=str(images_dir),
    minio=minio or MagicMock(),
    api=api or MagicMock(),
    rabbitmq=rabbitmq or MagicMock(),
  )


def test_handle_trigger_calls_pipeline_in_order(tmp_path):
  _make_png(tmp_path / "a.png", 100, 200)

  minio = MagicMock()
  minio.upload.return_value = "http://minio/images/fake.png"
  api = MagicMock()
  api.create.return_value = {"id": 1, "image_url": "http://minio/images/fake.png", "width": 100, "height": 200}
  rabbitmq = MagicMock()

  worker = _make_worker(tmp_path, minio=minio, api=api, rabbitmq=rabbitmq)
  worker._handle_trigger()

  minio.upload.assert_called_once()
  assert minio.upload.call_args[0][0].endswith("a.png")

  api.create.assert_called_once_with("http://minio/images/fake.png", 100, 200)

  rabbitmq.publish.assert_called_once()
  published = json.loads(rabbitmq.publish.call_args[0][0])
  assert published == {"id": 1, "image_url": "http://minio/images/fake.png", "width": 100, "height": 200}


def test_handle_trigger_cycles_through_images(tmp_path):
  _make_png(tmp_path / "a.png", 1, 1)
  _make_png(tmp_path / "b.png", 2, 2)

  minio = MagicMock()
  minio.upload.return_value = "url"
  api = MagicMock()
  api.create.return_value = {"id": 1, "image_url": "url", "width": 1, "height": 1}

  worker = _make_worker(tmp_path, minio=minio, api=api)
  worker._handle_trigger()
  worker._handle_trigger()
  worker._handle_trigger()

  paths = [call[0][0] for call in minio.upload.call_args_list]
  assert paths[0] != paths[1]
  assert paths[0] == paths[2]


def test_worker_raises_if_images_dir_is_empty(tmp_path):
  with pytest.raises(RuntimeError):
    _make_worker(tmp_path)