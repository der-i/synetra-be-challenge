import time

import requests


class ApiClient:
  def __init__(self, host: str, port: int, retries: int = 5, backoff: int = 2) -> None:
    self._url = f"http://{host}:{port}/objects"
    self._retries = retries
    self._backoff = backoff

  def create(self, image_url: str, width: int, height: int) -> dict:
    payload = {"image_url": image_url, "width": width, "height": height}
    last_error = None
    for attempt in range(1, self._retries + 1):
      try:
        response = requests.post(self._url, json=payload, timeout=5)
        response.raise_for_status()
        return response.json()
      except requests.RequestException as e:
        last_error = e
        print(f"API request failed (attempt {attempt}/{self._retries}): {e}")
        time.sleep(self._backoff)
    raise RuntimeError(f"Could not reach API at {self._url}: {last_error}")