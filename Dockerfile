FROM python:3.5

RUN apt-get update && apt-get -y install postgresql-client

RUN pip install -U pip==9.0.1

RUN pip install pip-tools

RUN mkdir /app

WORKDIR /app

ADD requirements.txt /app

RUN pip-sync requirements.txt

ADD . /app

RUN touch /app/.env

CMD ["python", "main.py"]
