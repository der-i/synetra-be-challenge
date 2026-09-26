import socket
import time


class TcpClient:
  TRIGGER = b"[s][save_image][e]"

  def __init__(self, host: str, port: int, on_trigger) -> None:
    self._host = host
    self._port = port
    self._on_trigger = on_trigger

  def run(self) -> None:
    while True:
      try:
        with socket.create_connection((self._host, self._port), timeout=10) as sock:
          print(f"Connected to TCP server {self._host}:{self._port}")
          self._read_loop(sock)
      except (ConnectionRefusedError, socket.timeout, OSError) as e:
        print(f"TCP connection error: {e}, retrying in 3s...")
      except Exception as e:
        print(f"Unexpected TCP client error: {e}")
      time.sleep(3)

  def _read_loop(self, sock: socket.socket) -> None:
    buffer = b""
    while True:
      data = sock.recv(1024)
      if not data:
        print("TCP server closed the connection")
        break
      buffer += data
      while self.TRIGGER in buffer:
        buffer = buffer.replace(self.TRIGGER, b"", 1)
        print("Got save_image trigger")
        try:
          self._on_trigger()
        except Exception as e:
          print(f"Error while handling trigger: {e}")