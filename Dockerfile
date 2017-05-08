FROM python:2.7

MAINTAINER Andrejs Lahs

RUN apt-get -y update
RUN apt-get -y upgrade

RUN apt-get -y install libgdal-dev

RUN mkdir -p /usr/src/app

COPY requirements.txt /usr/src/app/
COPY . /usr/src/app

WORKDIR /usr/src/app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]