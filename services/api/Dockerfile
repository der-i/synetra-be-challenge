FROM python:3.12-slim

WORKDIR /app

COPY services/api/requirements.txt ./

RUN pip install -r requirements.txt

COPY ./.env ./

COPY services/api/app/ ./

CMD [ "python", "-u", "main.py" ]