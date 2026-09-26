import time

from minio import Minio
from minio.error import S3Error


class MinioClient:
  def __init__(self, endpoint: str, public_endpoint: str, access_key: str, secret_key: str, bucket: str) -> None:
    self._client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=False)
    self._public_endpoint = public_endpoint
    self._bucket = bucket

  def upload(self, local_path: str, object_name: str, retries: int = 5, backoff: int = 3) -> str:
    last_error = None
    for attempt in range(1, retries + 1):
      try:
        self._client.fput_object(self._bucket, object_name, local_path)
        return f"http://{self._public_endpoint}/{self._bucket}/{object_name}"
      except S3Error as e:
        last_error = e
        print(f"MinIO upload failed (attempt {attempt}/{retries}): {e}")
        time.sleep(backoff)
    raise RuntimeError(f"Could not upload to MinIO: {last_error}")