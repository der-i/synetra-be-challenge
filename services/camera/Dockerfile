FROM python:3.12-slim

WORKDIR /app

COPY services/camera/requirements.txt ./

RUN pip install -r requirements.txt

COPY ./.env ./

COPY services/camera/app/ ./

CMD [ "python", "-u", "main.py" ]