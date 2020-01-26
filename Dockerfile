FROM python:3.6

COPY ./shelf_detector/requirements.txt /root/shelf_detector_requirements.txt
COPY ./ground_inspector/requirements.txt /root/ground_inspector_requirements.txt
COPY ./web_monitor/requirements.txt /root/web_monitor_requirements.txt


WORKDIR /app

RUN apt-get update -y

RUN apt-get install -y libjpeg62-turbo-dev zlib1g-dev
RUN apt-get install -y libzbar-dev

RUN pip install -r /root/shelf_detector_requirements.txt
RUN pip install -r /root/ground_inspector_requirements.txt
RUN pip install -r /root/web_monitor_requirements.txt


EXPOSE 5002

CMD python ./web_monitor/index.py
