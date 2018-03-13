FROM ubuntu:16.04
RUN apt-get update
RUN apt-get install -y python-pip
RUN pip install cherrypy  jinja2 mysql-connector-python

VOLUME /app
EXPOSE 8080

CMD cd /app && python  main.py
