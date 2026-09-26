import subprocess
import time

import pytest
import requests

pytestmark = pytest.mark.e2e

API_URL = "http://localhost:8000"
RABBITMQ_QUEUE_API = "http://localhost:15672/api/queues/%2F/inference.in"
RABBITMQ_AUTH = ("guest", "guest123")


@pytest.fixture(scope="module")
def running_stack():
  subprocess.run(["docker", "compose", "up", "-d", "--build"], check=True)
  _wait_for_api()
  yield
  subprocess.run(["docker", "compose", "down"], check=True)


def _wait_for_api(timeout: int = 60) -> None:
  deadline = time.time() + timeout
  while time.time() < deadline:
    try:
      if requests.get(f"{API_URL}/objects", timeout=2).status_code == 200:
        return
    except requests.RequestException:
      pass
    time.sleep(1)
  raise TimeoutError("api did not become ready in time")


def test_trigger_produces_record_object_and_message(running_stack):
  baseline_ids = {r["id"] for r in requests.get(f"{API_URL}/objects").json()}

  new_record = None
  deadline = time.time() + 30
  while time.time() < deadline:
    current = requests.get(f"{API_URL}/objects").json()
    new_ones = [r for r in current if r["id"] not in baseline_ids]
    if new_ones:
      new_record = new_ones[0]
      break
    time.sleep(1)

  assert new_record is not None, "camera did not produce a new record in time"

  image_resp = requests.head(new_record["image_url"], timeout=5)
  assert image_resp.status_code == 200

  messages = _wait_for_queue_messages(min_count=1)
  assert messages >= 1


def _wait_for_queue_messages(min_count: int, timeout: int = 15) -> int:
  deadline = time.time() + timeout
  last = 0
  while time.time() < deadline:
    resp = requests.get(RABBITMQ_QUEUE_API, auth=RABBITMQ_AUTH, timeout=5)
    if resp.status_code == 200:
      last = resp.json().get("messages", 0)
      if last >= min_count:
        return last
    time.sleep(1)
  raise AssertionError(f"queue did not reach {min_count} message(s) within {timeout}s (last seen: {last})")