import os
import sys

from dotenv import load_dotenv
from pipeline.api_client import ApiClient
from pipeline.minio_client import MinioClient
from pipeline.rabbitmq_client import RabbitMqClient
from worker import Worker


def main():
  try:
    load_dotenv()

    tcp_host = os.getenv("TCP_HOST", "checker")
    tcp_port = int(os.getenv("TCP_PORT", 4096))
    ws_host = "0.0.0.0"
    ws_port = int(os.getenv("WS_PORT", 1234))
    images_dir = os.getenv("IMAGES_DIR", "/data/images")

    api_host = os.getenv("API_HOST", "api")
    api_port = int(os.getenv("API_PORT", 8000))

    minio_endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
    minio_public_endpoint = os.getenv("MINIO_PUBLIC_ENDPOINT", minio_endpoint)
    minio_bucket = os.getenv("MINIO_BUCKET", "images")
    minio_user = os.getenv("MINIO_ROOT_USER")
    minio_password = os.getenv("MINIO_ROOT_PASSWORD")

    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER")
    rabbitmq_password = os.getenv("RABBITMQ_DEFAULT_PASS")

    minio = MinioClient(minio_endpoint, minio_public_endpoint, minio_user, minio_password, minio_bucket)
    api = ApiClient(api_host, api_port)
    rabbitmq = RabbitMqClient(rabbitmq_host, rabbitmq_user, rabbitmq_password)

    worker = Worker(
      tcp_host=tcp_host,
      tcp_port=tcp_port,
      ws_host=ws_host,
      ws_port=ws_port,
      images_dir=images_dir,
      minio=minio,
      api=api,
      rabbitmq=rabbitmq,
    )
    worker.run()
  except Exception as e:
    print(f"Error occurred: {e}")
    sys.exit(1)


if __name__ == "__main__":
  main()