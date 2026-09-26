import time

import pika


class RabbitMqClient:
  def __init__(
    self,
    host: str,
    user: str,
    password: str,
    exchange: str = "inference.in",
    routing_key: str = "inference.in",
  ) -> None:
    self._host = host
    self._credentials = pika.PlainCredentials(user, password)
    self._exchange = exchange
    self._routing_key = routing_key
    self._connection = None
    self._channel = None

  def _ensure_connection(self) -> None:
    if self._connection is not None and self._connection.is_open:
      return
    params = pika.ConnectionParameters(host=self._host, credentials=self._credentials)
    self._connection = pika.BlockingConnection(params)
    self._channel = self._connection.channel()

  def publish(self, message: str, retries: int = 5, backoff: int = 3) -> None:
    for attempt in range(1, retries + 1):
      try:
        self._ensure_connection()
        self._channel.basic_publish(
          exchange=self._exchange,
          routing_key=self._routing_key,
          body=message.encode("utf-8"),
        )
        return
      except Exception as e:
        print(f"RabbitMQ publish failed (attempt {attempt}/{retries}): {e}")
        self._connection = None
        time.sleep(backoff)
    print(f"Giving up publishing to RabbitMQ after {retries} attempts")