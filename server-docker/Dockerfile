FROM python:3.11.3

WORKDIR /app

COPY ../ /app/

RUN pip install -r ./server-docker/requirements.txt

ENTRYPOINT [ "python", "server.py" ]
