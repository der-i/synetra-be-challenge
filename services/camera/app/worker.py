import json
import uuid
from itertools import cycle
from pathlib import Path
from threading import Thread

from pipeline.api_client import ApiClient
from pipeline.image_meta import get_png_size
from pipeline.minio_client import MinioClient
from pipeline.rabbitmq_client import RabbitMqClient
from tcp.client import TcpClient
from ws.server import WsServer


class Worker:
  def __init__(
    self,
    tcp_host: str,
    tcp_port: int,
    ws_host: str,
    ws_port: int,
    images_dir: str,
    minio: MinioClient,
    api: ApiClient,
    rabbitmq: RabbitMqClient,
  ) -> None:
    images = sorted(p for p in Path(images_dir).iterdir() if p.suffix.lower() == ".png")
    if not images:
      raise RuntimeError(f"No PNG images found in {images_dir}")
    self._images = cycle(images)

    self._minio = minio
    self._api = api
    self._rabbitmq = rabbitmq

    self._ws = WsServer(ws_host, ws_port)
    self._tcp = TcpClient(tcp_host, tcp_port, self._handle_trigger)

  def _handle_trigger(self) -> None:
    path = next(self._images)
    object_name = f"{uuid.uuid4()}_{path.name}"
    width, height = get_png_size(str(path))

    image_url = self._minio.upload(str(path), object_name)
    record = self._api.create(image_url, width, height)

    message = json.dumps({"id": record["id"], "image_url": image_url, "width": width, "height": height})
    self._ws.broadcast(message)
    self._rabbitmq.publish(message)
    print(f"Processed {path.name} -> {image_url}")

  def run(self) -> None:
    tcp_thread = Thread(target=self._tcp.run, daemon=True)
    ws_thread = Thread(target=self._ws.run, daemon=True)

    tcp_thread.start()
    ws_thread.start()

    tcp_thread.join()
    ws_thread.join()