FROM python:2.7

MAINTAINER Piotr Bajsarowicz <piotr.bajsarowicz@gmail.com>

RUN mkdir -p /home/app/rush
COPY requirements.pip /home/app/
RUN pip install -r /home/app/requirements.pip

ENV DJANGO_SETTINGS_MODULE=rush.local_settings

EXPOSE 8000

WORKDIR /home/app/rush
ENTRYPOINT ["python","manage.py"]
CMD ["runserver","0.0.0.0:8000"]
