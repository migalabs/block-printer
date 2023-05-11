FROM python:3.11.3

WORKDIR /app

COPY ../ /app/

RUN pip install -r ./load-db-docker/requirements.txt

ENTRYPOINT [ "python", "load_db.py" ]
