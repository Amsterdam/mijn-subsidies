FROM amsterdam/python

LABEL maintainer=datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1
ENV REQUESTS_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt

RUN apt-get update && apt-get install -y
RUN pip install --upgrade pip
RUN pip install uwsgi

WORKDIR /app

COPY app ./app
COPY scripts ./scripts
COPY requirements.txt .
COPY uwsgi.ini .

COPY /test.sh /app
COPY .flake8 .
COPY *.pem /usr/local/share/ca-certificates/extras/
RUN chmod -R 644 /usr/local/share/ca-certificates/extras/ \
  && update-ca-certificates

RUN pip install --no-cache-dir -r /app/requirements.txt

USER datapunt
CMD uwsgi --ini /app/uwsgi.ini
