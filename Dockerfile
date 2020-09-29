FROM python:3.8-alpine

RUN adduser -D homeshop

WORKDIR /home/homeshop

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn pymysql

COPY app app
COPY migrations migrations
COPY project.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP project.py

RUN chown -R homeshop:homeshop ./
USER homeshop

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]